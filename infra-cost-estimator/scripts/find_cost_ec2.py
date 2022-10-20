"""Get EC2 and EBS storage cost"""
import csv
import json
import boto3

from find_instance_family import find_instance_family
from find_operating_system import find_operating_system
from find_region import find_region
from find_values import find_values_from_key, find_values_containing_substring


def find_ec2_cost(obj):
    """
    Function to get EC2 cost.
    Receive 1 terraform plan json object as parameter.
    Return operating_system, market_option, instance_type, ec2_unit, monthly_ec2_price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')
    ec2 = boto3.client('ec2')

    try:
        ami_id = find_values_from_key('image_id', obj)[0]
        ami_details = ec2.describe_images(ImageIds=[ami_id])
        ami_platform_details = ami_details['Images'][0]['PlatformDetails']
        operating_system = find_operating_system(ami_platform_details)
    except:
        operating_system = 'Linux'

    region_id = find_region(obj)
    instance_type = find_values_from_key('instance_type', obj)[0]
    instance_family = find_instance_family(instance_type)
    market_option = 'OnDemand'
    pre_installed_sw = 'NA'

    response = pricing.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Compute Instance'},
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': operating_system},
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
            {'Type': 'TERM_MATCH', 'Field': 'instanceFamily', 'Value': instance_family},
            {'Type': 'TERM_MATCH', 'Field': 'marketoption', 'Value': market_option},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': pre_installed_sw}
        ],
        MaxResults=1
    )

    ec2_unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    hourly_ec2_price = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    monthly_ec2_price = hourly_ec2_price * 720
    return operating_system, market_option, instance_type, ec2_unit, monthly_ec2_price


def find_ebs_cost(obj):
    """
    Function to get EBS cost.
    Receive 1 terraform plan json object as parameter.
    Return volume_type, volume_api_name, volume_size, ebs_unit, monthly_ebs_price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')

    region_id = find_region(obj)
    volume_api_name = find_values_from_key('volume_type', obj)[0]
    volume_size = find_values_from_key('volume_size', obj)[0]

    response = pricing.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': "storage"},
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'volumeApiName', 'Value': volume_api_name}
        ],
        MaxResults=1
    )

    volume_type = find_values_from_key('volumeType', json.loads(response['PriceList'][0]))[0]
    ebs_unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    monthly_ebs_price = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD']) * float(volume_size)
    monthly_ebs_price = f'{monthly_ebs_price:.2f}'

    return volume_type, volume_api_name, volume_size, ebs_unit, monthly_ebs_price

def calculate_ec2_and_ebs(address_param, file_obj):
    """
    Calculate EC2 cost, EBS cost, and then write to data.csv
    """
    address = find_values_containing_substring("address", address_param, file_obj)[0]
    operating_system, market_option, instance_type, ec2_unit, monthly_ec2_price = find_ec2_cost(file_obj)
    volume_type, volume_api_name, volume_size, ebs_unit, monthly_ebs_price = find_ebs_cost(file_obj)

    fields = [
        [' ', ' ', ' ', ' '],
        [address, ' ', ' ', ' '],
        [f'├── Instance usage ({operating_system}, {market_option}, {instance_type})', 720, f'{ec2_unit}', f'${monthly_ec2_price}'],
        [f'└── Storage ({volume_type}, {volume_api_name})', f'{volume_size}', f'{ebs_unit}', f'${monthly_ebs_price}']
    ]

    with open(r'/usr/local/bin/infra-cost-estimator/data/data.csv', 'a', encoding="utf-8") as file:
        writer = csv.writer(file)
        for field in fields:
            writer.writerow(field)

    return float(monthly_ec2_price) + float(monthly_ebs_price)
