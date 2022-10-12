"""Get ASG's instances and EBS storage cost"""
import csv
import json
import sys
import boto3

from find_instance_family import find_instance_family
from find_operating_system import find_operating_system
from find_region import find_region
from find_values import find_values_from_key, find_values_containing_substring


def find_asg_cost(obj):
    """
    Function to get ASG cost.
    Receive 1 terraform plan json object as parameter.
    Return operating_system, market_option, instance_type, asg_min_size, asg_max_size, unit, range_price_per_month
    """
    pricing = boto3.client('pricing', region_name='us-east-1')
    ec2 = boto3.client('ec2')
    
    try:
        ami_id = find_values_from_key('image_id', obj['planned_values']['root_module']['child_modules'])[0]
        ami_details = ec2.describe_images(ImageIds=[ami_id])
        ami_platform_details = ami_details['Images'][0]['PlatformDetails']
        operating_system = find_operating_system(ami_platform_details)
    except:
        operating_system = 'Linux'

    region_id = find_region(obj)
    instance_type = find_values_from_key('instance_type', obj['planned_values']['root_module']['child_modules'])[0]
    instance_family = find_instance_family(instance_type)
    market_option = 'OnDemand'
    pre_installed_sw = 'NA'
    asg_max_size = find_values_from_key('max_size', obj['planned_values']['root_module']['child_modules'])[0]
    asg_min_size = find_values_from_key('min_size', obj['planned_values']['root_module']['child_modules'])[0]

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

    unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    hourly_ec2_price = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    monthly_ec2_price = hourly_ec2_price * 720

    lower_bound = float(asg_min_size) * monthly_ec2_price
    upper_bound = float(asg_max_size) * monthly_ec2_price
    range_price_per_month = f"{lower_bound:.2f} ~ {upper_bound:.2f}"
    return operating_system, market_option, instance_type, asg_min_size, asg_max_size, unit, range_price_per_month


def find_ebs_cost(obj):
    """
    Function to get EBS cost.
    Receive 1 terraform plan json object as parameter.
    Return volume_type, volume_api_name, volume_size, unit, monthly_ebs_price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')

    region_id = find_region(obj)
    volume_api_name = find_values_from_key('volume_type', obj['planned_values']['root_module']['child_modules'])[0]
    volume_size = find_values_from_key('volume_size', obj['planned_values']['root_module']['child_modules'])[0]

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
    unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    monthly_ebs_price = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD']) * volume_size
    monthly_ebs_price = f'{monthly_ebs_price:.2f}'

    return volume_type, volume_api_name, volume_size, unit, monthly_ebs_price


# Open xxxxxx-app-plan.json file and create obj dictionary
with open(sys.argv[1], encoding="utf-8") as file:
    file_obj = json.load(file)

address = find_values_containing_substring("address", ".aws_autoscaling_group.", file_obj)[0]
asg_cost = find_asg_cost(file_obj)
ebs_cost = find_ebs_cost(file_obj)

fields_1 = [' ', ' ', ' ', ' ']
fields_2 = [address, ' ', ' ', ' ']
fields_3 = [f'├── Instance usage ({asg_cost[0]}, {asg_cost[1]}, {asg_cost[2]})', 720, f'{asg_cost[5]}', f'${asg_cost[6]}']
fields_4 = [f'└── Storage ({ebs_cost[0]}, {ebs_cost[1]})', f'{ebs_cost[2]}', f'{ebs_cost[3]}', f'${ebs_cost[4]}']

with open(r'/usr/local/bin/infra-cost-estimator/data/data.csv', 'a', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(fields_1)
    writer.writerow(fields_2)
    writer.writerow(fields_3)
    writer.writerow(fields_4)
