"""Get RDS's instance and storage cost"""
import csv
import json
import boto3

from find_database_engine import find_engine
from find_instance_family import find_instance_family
from find_region import find_region
from find_values import find_values_from_key, find_values_containing_substring


def find_rds_instance_cost(obj):
    """
    Function to get RDS instance cost.
    Receive 1 Terraform plan JSON object as parameter.
    Return instance_type, database_engine, deployment_option, rds_instance_unit, monthly_rds_instance_cost
    """

    pricing = boto3.client('pricing', region_name='us-east-1')

    region_id = find_region(obj)
    instance_type = find_values_from_key('instance_class', obj['planned_values'])[0]
    instance_family = find_instance_family(instance_type[3:])
    engine = find_values_from_key('engine', obj['planned_values'])[0]
    database_engine = find_engine(engine)
    multi_az = find_values_from_key('multi_az', obj['planned_values'])[0]
    deployment_option = "Multi-AZ" if multi_az else "Single-AZ"

    response = pricing.get_products(
        ServiceCode='AmazonRDS',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': "Database Instance"},
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
            {'Type': 'TERM_MATCH', 'Field': 'instanceFamily', 'Value': instance_family},
            {'Type': 'TERM_MATCH', 'Field': 'databaseEngine', 'Value': database_engine},
            {'Type': 'TERM_MATCH', 'Field': 'deploymentOption', 'Value': deployment_option},
        ],
        MaxResults=1
    )

    rds_instance_unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    hourly_rds_instance_price = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    monthly_rds_instance_cost = f'{hourly_rds_instance_price * 720:.2f}'
    return instance_type, database_engine, deployment_option, rds_instance_unit, monthly_rds_instance_cost


def find_rds_storage_cost(obj):
    """
    Function to get RDS storage cost.
    Receive 1 Terraform plan JSON object as parameter.
    Return volume_type, volume_api_name, deployment_option, allocated_storage, rds_storage_unit, monthly_rds_storage_cost
    """

    pricing = boto3.client('pricing', region_name='us-east-1')

    region_id = find_region(obj)
    engine = find_values_from_key('engine', obj['planned_values'])[0]
    database_engine = find_engine(engine)
    multi_az = find_values_from_key('multi_az', obj['planned_values'])[0]
    deployment_option = "Multi-AZ" if multi_az else "Single-AZ"
    allocated_storage = find_values_from_key('allocated_storage', obj['planned_values'])[0]
    volume_api_name = find_values_from_key('storage_type', obj['planned_values']['root_module']['child_modules'])[0]

    response = pricing.get_products(
        ServiceCode='AmazonRDS',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': "Database Storage"},
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'databaseEngine', 'Value': database_engine},
            {'Type': 'TERM_MATCH', 'Field': 'deploymentOption', 'Value': deployment_option},
        ],
        MaxResults=1
    )

    volume_type = find_values_from_key('volumeType', json.loads(response['PriceList'][0]))[0]
    rds_storage_unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    monthly_rds_storage_cost = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD']) * allocated_storage
    monthly_rds_storage_cost = f'{monthly_rds_storage_cost:.2f}'
    return volume_type, volume_api_name, deployment_option, allocated_storage, rds_storage_unit, monthly_rds_storage_cost

def calculate_rds(address_param, file_obj):
    """
    Calculate RDS instance cost, RDSstorage cost, and then write to data.csv
    """
    address = find_values_containing_substring("address", address_param, file_obj)[0]
    instance_type, database_engine, deployment_option, rds_instance_unit, monthly_rds_instance_cost = find_rds_instance_cost(file_obj)
    volume_type, volume_api_name, deployment_option, allocated_storage, rds_storage_unit, monthly_rds_storage_cost = find_rds_storage_cost(file_obj)

    fields = [
        [' ', ' ', ' ', ' '],
        [address, ' ', ' ', ' '],
        [f'├── Database instance ({instance_type}, {database_engine}, {deployment_option})',
                720, f'{rds_instance_unit}', f'${monthly_rds_instance_cost}'],
        [f'└── Storage ({volume_type}, {volume_api_name}, {deployment_option})',
                f'{allocated_storage}', f'{rds_storage_unit}', f'${monthly_rds_storage_cost}']   
    ]

    with open(r'/usr/local/bin/infra-cost-estimator/data/data.csv', 'a', encoding="utf-8") as file:
        writer = csv.writer(file)
        for field in fields:
            writer.writerow(field)

    return float(monthly_rds_instance_cost) + float(monthly_rds_storage_cost)
