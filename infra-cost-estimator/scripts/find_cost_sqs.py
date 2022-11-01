"""Get SQS storage cost"""
import csv
import json
import boto3

from find_region import find_region
from find_values import find_values_from_key, find_values_containing_substring

def find_sqs_cost(obj):
    """
    Function to get SQS cost.
    Receive 1 terraform plan json object as parameter.
    Return monthly_qty, queue_type, unit, price_per_unit, monthly_sqs_price
    """
    pricing = boto3.client('pricing', region_name='us-east-1')

    fifo = find_values_from_key('fifo_queue', obj['planned_values']['root_module']['resources'])[0]

    if fifo is not False:
        queue_type = "FIFO (first-in, first-out)"
        monthly_qty = 28273
    else :
        queue_type = "Standard"
        monthly_qty = 25959083
    region_id = find_region(obj)

    response = pricing.get_products(
        ServiceCode='AWSQueueService',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'API Request'},
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'queueType', 'Value': queue_type},
        ],
        MaxResults=1
    )

    unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    price_per_unit = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    if monthly_qty < 1000000 :
        monthly_sqs_price = 0
    else :
        monthly_sqs_price = price_per_unit * (monthly_qty - 1000000)
    return monthly_qty, queue_type, unit, price_per_unit, monthly_sqs_price


def calculate_sqs(address_param, file_obj):

    address = find_values_containing_substring("address", address_param, file_obj)[0]
    sqs_cost = find_sqs_cost(file_obj)

    fields_1 = [' ', ' ', ' ', ' ']
    fields_2 = [address, ' ', ' ', ' ']
    fields_3 = [f'└── SQS {sqs_cost[1]}', 'Depends on usage' , f'{sqs_cost[2]}', f'${sqs_cost[3]}']
    fields_4 = [' ', f'└── Example: {sqs_cost[0]}', f'{sqs_cost[2]}', f'${sqs_cost[4]:.2f}']

    with open(r'/usr/local/bin/infra-cost-estimator/data/data.csv', 'a', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(fields_1)
        writer.writerow(fields_2)
        writer.writerow(fields_3)
        writer.writerow(fields_4)

    return float(sqs_cost[3])
