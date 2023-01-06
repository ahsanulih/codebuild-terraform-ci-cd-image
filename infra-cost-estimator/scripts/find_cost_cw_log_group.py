"""Get Cloudwatch Log Group cost"""
import csv
import json
import boto3

from find_region import find_region
from find_values import find_values_from_key, find_values_containing_substring


def find_cwl_data_ingested_cost(obj):
    """
    Function to get Cloudwatch log group data ingested cost.
    Receive 1 terraform plan json object as parameter.
    Return return cwl_data_ingested_unit, cwl_data_ingested_price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')
    region_id = find_region(obj)

    response = pricing.get_products(
        ServiceCode='AmazonCloudwatch',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Data Payload'},
            {'Type': 'TERM_MATCH', 'Field': 'group', 'Value': 'Ingested Logs'},
        ],
        MaxResults=1
    )

    cwl_data_ingested_unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    cwl_data_ingested_price = float(find_values_from_key('pricePerUnit',json.loads(response['PriceList'][0]))[0]['USD'])
    return cwl_data_ingested_unit, cwl_data_ingested_price


def find_cwl_archival_storage_cost(obj):
    """
    Function to get Cloudwatch log group archival storage cost.
    Receive 1 terraform plan json object as parameter.
    Return cwl_archival_storage_unit, cwl_archival_storage_price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')
    region_id = find_region(obj)

    response = pricing.get_products(
        ServiceCode='AmazonCloudwatch',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Storage Snapshot'}
        ],
        MaxResults=1
    )

    cwl_archival_storage_unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    cwl_archival_storage_price = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    return cwl_archival_storage_unit, cwl_archival_storage_price


def find_cwl_insight_queries_data_scanned_cost(obj):
    """
    Function to get Cloudwatch log group insight queries data scanned cost.
    Receive 1 terraform plan json object as parameter.
    Return unit, price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')
    region_id = find_region(obj)

    response = pricing.get_products(
        ServiceCode='AmazonCloudwatch',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Data Payload'},
            {'Type': 'TERM_MATCH', 'Field': 'group', 'Value': 'Queried Logs'}
        ],
        MaxResults=1
    )

    cwl_insight_queries_data_scanned_unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    cwl_insight_queries_data_scanned_price = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    return cwl_insight_queries_data_scanned_unit, cwl_insight_queries_data_scanned_price


def calculate_cwl(address_param, file_obj):
    """
    Calculate Cloudwatch Log Group cost and then write to data.csv
    """
    address = find_values_containing_substring("address", address_param, file_obj)[0]

    cwl_data_ingested_unit, cwl_data_ingested_price = find_cwl_data_ingested_cost(file_obj)
    cwl_archival_storage_unit, cwl_archival_storage_price = find_cwl_archival_storage_cost(file_obj)
    cwl_insight_queries_data_scanned_unit, cwl_insight_queries_data_scanned_price = find_cwl_insight_queries_data_scanned_cost(file_obj)

    fields = [
        [' ', ' ', ' ', ' '],
        [address, ' ', ' ', ' '],
        ['├── Data ingested', 'Depends on usage', f'{cwl_data_ingested_unit}', f'${cwl_data_ingested_price}'],
        ['│', '└── Example: 1432', f'{cwl_data_ingested_unit}', f'${(1432 * cwl_data_ingested_price):.2f}'],
        ['├── Archival storage', 'Depends on usage', f'{cwl_archival_storage_unit}', f'${cwl_archival_storage_price}'],
        ['│', '└── Example: 132.66', f'{cwl_archival_storage_unit}', f'${(132.66 * cwl_archival_storage_price):.2f}'],
        ['└── Insights queries data scanned', 'Depends on usage', f'{cwl_insight_queries_data_scanned_unit}', f'${cwl_insight_queries_data_scanned_price}'],
        [' ', '└── Example: 1148.33', f'{cwl_insight_queries_data_scanned_unit}', f'${(1148.33 * cwl_insight_queries_data_scanned_price):.2f}']
    ]

    with open(r'/usr/local/bin/infra-cost-estimator/data/data.csv', 'a', encoding="utf-8") as file:
        writer = csv.writer(file)
        for field in fields:
            writer.writerow(field)

    return 0
