"""Function to get RDS cost"""

import json
import sys
import boto3
import pandas as pd
from tabulate import tabulate

from infra_cost_find_values import find_values
from infra_cost_find_region import find_region
from infra_cost_find_instance_family import find_instance_family
from infra_cost_find_database_engine import find_engine

def find_rds_prices(obj):
    """
    Function to get RDS cost.
    Receive 1 Terraform plan JSON object as parameter.
    Return instanceType, allocated_storage, multi_az, instance_price_per_month,
    storage_price_per_month, total_cost_per_month
    """

    pricing = boto3.client('pricing', region_name='us-east-1')

    location = find_region(obj)
    instance_type = find_values('instance_class', obj['planned_values'])[0]
    instance_family = find_instance_family(instance_type[3:])
    engine = find_values('engine', obj['planned_values'])[0]
    database_engine = find_engine(engine)
    multi_az = find_values('multi_az', obj['planned_values'])[0]
    allocated_storage = find_values('allocated_storage', obj['planned_values'])[0]
    storage_per_gb_cost = 0.138 # Temporarily hardcoded because AWS pricing API doesn't provide this data
    print("Service : RDS")
    print("Region  : " + location)
    response = pricing.get_products(
        ServiceCode='AmazonRDS',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': location},
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
            {'Type': 'TERM_MATCH', 'Field': 'instanceFamily', 'Value': instance_family},
            {'Type': 'TERM_MATCH', 'Field': 'databaseEngine', 'Value': database_engine},
        ],
        MaxResults=1
    )

    instance_price_per_hour = float(find_values('pricePerUnit', json.loads(
        response['PriceList'][0]))[0]['USD'])
    instance_price_per_month = instance_price_per_hour * 720
    storage_price_per_month = allocated_storage * storage_per_gb_cost
    total_cost_per_month = instance_price_per_month + storage_price_per_month
    return instance_type, database_engine, allocated_storage, multi_az, \
        instance_price_per_month, storage_price_per_month, total_cost_per_month

# Open xxxxxx-postgres-plan.json file and create obj dictionary
with open(sys.argv[1], encoding="utf-8") as file:
    file_obj = json.load(file)

rds_cost = find_rds_prices(file_obj)
rds_price_data = rds_cost
rds_df = pd.DataFrame(rds_price_data)  # convert rds_price_data to pandas dataframe
rds_df = rds_df.transpose()  # converting rows to columns
rds_df.index += 1  # start index from 1
rds_df.columns = ["Instance Type", "Engine", "Storage(GB)", "Multi AZ", "Instance monthly cost(USD)",
                  "Storage monthly cost(USD)", "Total monthly cost(USD)"]
print(tabulate(rds_df, headers=rds_df.columns, tablefmt='psql'))
