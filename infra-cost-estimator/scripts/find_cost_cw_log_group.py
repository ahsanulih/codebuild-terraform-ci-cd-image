"""Get Cloudwatch Log Group cost"""
import csv
import json
import sys
import boto3

from find_region import find_region
from find_values import find_values_from_key, find_values_containing_substring


def find_cwl_data_ingested_cost(obj):
    """
    Function to get Cloudwatch log group data ingested cost.
    Receive 1 terraform plan json object as parameter.
    Return unit, price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')
    region_id = find_region(obj)[0]

    response = pricing.get_products(
        ServiceCode='AmazonCloudwatch',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Data Payload'},
            {'Type': 'TERM_MATCH', 'Field': 'group', 'Value': 'Ingested Logs'},
        ],
        MaxResults=1
    )

    unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    price = float(find_values_from_key('pricePerUnit',json.loads(response['PriceList'][0]))[0]['USD'])
    return unit, price


def find_cwl_archival_storage_cost(obj):
    """
    Function to get Cloudwatch log group archival storage cost.
    Receive 1 terraform plan json object as parameter.
    Return unit, price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')
    region_id = find_region(obj)[0]

    response = pricing.get_products(
        ServiceCode='AmazonCloudwatch',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Storage Snapshot'}
        ],
        MaxResults=1
    )

    unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    price = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    return unit, price


def find_cwl_insight_queries_data_scanned_cost(obj):
    """
    Function to get Cloudwatch log group insight queries data scanned cost.
    Receive 1 terraform plan json object as parameter.
    Return unit, price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')
    region_id = find_region(obj)[0]

    response = pricing.get_products(
        ServiceCode='AmazonCloudwatch',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Data Payload'},
            {'Type': 'TERM_MATCH', 'Field': 'group', 'Value': 'Queried Logs'}
        ],
        MaxResults=1
    )

    unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    price = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    return unit, price


# Open xxxxxx-app-plan.json file and create obj dictionary
with open(sys.argv[1], encoding="utf-8") as file:
    file_obj = json.load(file)

addresses = find_values_containing_substring("address", ".aws_cloudwatch_log_group.", file_obj['planned_values'])

for address in addresses:
    cwl_data_ingested_cost = find_cwl_data_ingested_cost(file_obj)
    cwl_archival_storage_cost = find_cwl_archival_storage_cost(file_obj)
    cwl_insight_queries_data_scanned_cost = find_cwl_insight_queries_data_scanned_cost(file_obj)

    fields_1 = [' ', ' ', ' ', ' ']
    fields_2 = [address, ' ', ' ', ' ']
    fields_3 = ['├── Data ingested', 'Depends on usage', f'{cwl_data_ingested_cost[0]}', f'${cwl_data_ingested_cost[1]}']
    fields_4 = ['├── Archival storage', 'Depends on usage', f'{cwl_archival_storage_cost[0]}', f'${cwl_archival_storage_cost[1]}']
    fields_5 = ['└── Insights queries data scanned', 'Depends on usage', f'{cwl_insight_queries_data_scanned_cost[0]}', f'${cwl_insight_queries_data_scanned_cost[1]}']

    with open(r'/usr/local/bin/infra-cost-estimator/data/data.csv', 'a', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(fields_1)
        writer.writerow(fields_2)
        writer.writerow(fields_3)
        writer.writerow(fields_4)
        writer.writerow(fields_5)
