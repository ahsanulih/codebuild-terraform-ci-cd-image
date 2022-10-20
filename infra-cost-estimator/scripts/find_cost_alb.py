"""Get ALB and LCU cost"""
import csv
import json
import boto3

from find_region import find_region
from find_values import find_values_from_key, find_values_containing_substring


def find_alb_cost(obj):
    """
    Function to get ALB cost.
    Receive 1 terraform plan json object as parameter.
    Return alb_unit, hourly_alb_price, monthly_alb_price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')
    region_id = find_region(obj)
    response = pricing.get_products(
        ServiceCode='AWSELB',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Load Balancer-Application'},
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'groupDescription', 'Value': 'LoadBalancer hourly usage by Application Load Balancer'}
        ],
        MaxResults=1
    )

    alb_unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    hourly_alb_price = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    monthly_alb_price = f'{(hourly_alb_price * 720):.2f}'
    return alb_unit, hourly_alb_price, monthly_alb_price


def find_lcu_cost(obj):
    """
    Function to get LCU cost.
    Receive 1 terraform plan json object as parameter.
    Return lcu_unit, hourly_lcu_price, monthly_lcu_price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')
    region_id = find_region(obj)
    response = pricing.get_products(
        ServiceCode='AWSELB',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Load Balancer-Application'},
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'groupDescription', 'Value': 'Used Application Load Balancer capacity units-hr'}
        ],
        MaxResults=1
    )

    lcu_unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    hourly_lcu_price = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    monthly_lcu_price = f'{(hourly_lcu_price * 720):.2f}'
    return lcu_unit, hourly_lcu_price, monthly_lcu_price


def calculate_alb_and_lcu(address_param, file_obj):
    """
    Calculate ALB cost, LCU cost, and then write to data.csv
    """
    address = find_values_containing_substring("address", address_param, file_obj)[0]
    alb_unit, hourly_alb_price, monthly_alb_price = find_alb_cost(file_obj)
    lcu_unit, hourly_lcu_price, monthly_lcu_price = find_lcu_cost(file_obj)

    fields = [
        [' ', ' ', ' ', ' '],
        [address, ' ', ' ', ' '],
        ['├── Application Load Balancer', 720, alb_unit, f'${monthly_alb_price}'],
        ['└── Load balancer capacity unit', 'Depends on usage', lcu_unit, f'${hourly_lcu_price}']
    ]

    with open(r'/usr/local/bin/infra-cost-estimator/data/data.csv', 'a', encoding="utf-8") as file:
        writer = csv.writer(file)
        for field in fields:
            writer.writerow(field)

    return float(monthly_alb_price)
