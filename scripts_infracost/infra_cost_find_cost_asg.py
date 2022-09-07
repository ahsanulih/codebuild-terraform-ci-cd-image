"""Function to get ASG cost"""
import json
import sys
import boto3
import pandas as pd
from tabulate import tabulate

from infra_cost_find_values import find_values
from infra_cost_find_region import find_region
from infra_cost_find_instance_family import find_instance_family

def find_asg_cost(obj):
    """
    Function to get ASG cost.
    Receive 1 terraform plan json object as parameter.
    Return instanceType, asg_max_size, asg_min_size, range_price_per_month
    """
    pricing = boto3.client('pricing', region_name='us-east-1')

    location = find_region(obj)
    instance_type = find_values('instance_type', obj['planned_values'])[0]
    asg_max_size = find_values('max_size', obj['planned_values'])[0]
    asg_min_size = find_values('min_size', obj['planned_values'])[0]
    operating_system = 'Linux' # By default stack module is using Linux
    instance_family = find_instance_family(instance_type)
    market_option = 'OnDemand'
    capacity_status = 'UnusedCapacityReservation'
    pre_installed_sw = 'NA'

    print("Service : ASG")
    print("Region  : " + location)
    response = pricing.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': operating_system},
            {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': location},
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
            {'Type': 'TERM_MATCH', 'Field': 'instanceFamily', 'Value': instance_family},
            {'Type': 'TERM_MATCH', 'Field': 'marketoption', 'Value': market_option},
            {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': capacity_status},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': pre_installed_sw}
        ],
        MaxResults=1
    )

    price_per_hour = float(find_values('pricePerUnit', json.loads(
        response['PriceList'][0]))[0]['USD'])
    price_per_month = price_per_hour * 720

    lower_bound = float(asg_min_size) * price_per_month
    upper_bound = float(asg_max_size) * price_per_month
    range_price_per_month = f"{lower_bound} ~ {upper_bound}"
    return instance_type, asg_min_size, asg_max_size, range_price_per_month

# Open xxxxxx-app-plan.json file and create obj dictionary
with open(sys.argv[1], encoding="utf-8") as file:
    file_obj = json.load(file)

asg_cost = find_asg_cost(file_obj)
asg_price_data = asg_cost
asg_df = pd.DataFrame(asg_price_data)  # convert asg_price_data to pandas dataframe
asg_df = asg_df.transpose()  # converting rows to columns
asg_df.index += 1  # start index from 1
asg_df.columns = ["Instance Type", "ASG min size", "ASG max size", "Monthly cost (USD)"]
print(tabulate(asg_df, headers=asg_df.columns, tablefmt='psql'))
