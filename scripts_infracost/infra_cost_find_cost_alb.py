"""Function to get ALB cost"""

import json
import sys
import boto3
import pandas as pd
from tabulate import tabulate

from infra_cost_find_values import find_values
from infra_cost_find_region import find_region

def find_alb_cost(obj):
    """
    Function to get ALB cost.
    Receive 1 terraform plan json object as parameter.
    Return lb_type, range_price_per_month
    """
    pricing = boto3.client('pricing', region_name='us-east-1')

    location = find_region(obj)
    lb_type = find_values('load_balancer_type', obj['planned_values'])[0]
    lb_price_per_hour = 0.0252 #Temporarily Hardcoded because AWS pricing API doesn't provide this data
    lb_price_per_month = lb_price_per_hour * 720
    traffic_cost_per_month = 0 #ToDo
    total_price_per_month = lb_price_per_month + traffic_cost_per_month

    print("Service : ALB")
    print("Region  : " + location)

    return lb_type, lb_price_per_month, traffic_cost_per_month, total_price_per_month

# Open xxxxxx-app-plan.json file and create obj dictionary
with open(sys.argv[1], encoding="utf-8") as file:
    file_obj = json.load(file)

alb_cost = find_alb_cost(file_obj)
alb_price_data = alb_cost
alb_df = pd.DataFrame(alb_price_data)  # convert alb_price_data to pandas dataframe
alb_df = alb_df.transpose()  # converting rows to columns
alb_df.index += 1  # start index from 1
alb_df.columns = ["LB Type", "LB Cost(USD)", "Traffic Cost(USD)", "Total Monthly cost (USD)"]
print(tabulate(alb_df, headers=alb_df.columns, tablefmt='psql'))
