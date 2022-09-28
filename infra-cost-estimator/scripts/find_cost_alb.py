"""Get ALB and LCU cost"""
import csv
import json
import sys
import boto3

from find_region import find_region
from find_values import find_values_from_key, find_values_containing_substring


def find_alb_cost(obj):
    """
    Function to get ALB cost.
    Receive 1 terraform plan json object as parameter.
    Return unit, hourly_alb_price, monthly_alb_price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')
    region_id = find_region(obj)[0]
    response = pricing.get_products(
        ServiceCode='AWSELB',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Load Balancer-Application'},
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'groupDescription', 'Value': 'LoadBalancer hourly usage by Application Load Balancer'}
        ],
        MaxResults=1
    )

    unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    hourly_alb_price = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    monthly_alb_price = hourly_alb_price * 720
    monthly_alb_price = f'{monthly_alb_price:.2f}'
    return unit, hourly_alb_price, monthly_alb_price


def find_lcu_cost(obj):
    """
    Function to get LCU cost.
    Receive 1 terraform plan json object as parameter.
    Return unit, hourly_lcu_price, monthly_lcu_price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')
    region_id = find_region(obj)[0]
    response = pricing.get_products(
        ServiceCode='AWSELB',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Load Balancer-Application'},
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'groupDescription', 'Value': 'Used Application Load Balancer capacity units-hr'}
        ],
        MaxResults=1
    )

    unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    hourly_lcu_price = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    monthly_lcu_price = hourly_lcu_price * 720
    monthly_lcu_price = f'{monthly_lcu_price:.2f}'
    return unit, hourly_lcu_price, monthly_lcu_price


# Open xxxxxx-app-plan.json file and create obj dictionary
with open(sys.argv[1], encoding="utf-8") as file:
    file_obj = json.load(file)

address = find_values_containing_substring("address", ".aws_lb.", file_obj)[0]
alb_cost = find_alb_cost(file_obj)
lcu_cost = find_lcu_cost(file_obj)

fields_1 = [' ', ' ', ' ', ' ']
fields_2 = [address, ' ', ' ', ' ']
fields_3 = ['├── Application Load Balancer', 720, f'{alb_cost[0]}', f'${alb_cost[2]}']
fields_4 = ['└── Load balancer capacity unit', 'Depends on usage', f'{alb_cost[0]}', f'${lcu_cost[1]}']

with open(r'/usr/local/bin/infra-cost-estimator/data/data.csv', 'a', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(fields_1)
    writer.writerow(fields_2)
    writer.writerow(fields_3)
    writer.writerow(fields_4)
