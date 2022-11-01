"""Get S3 cost"""
import csv
import json
from lib2to3.pgen2.parse import ParseError
import sys
import boto3

from find_region import find_region
from find_values import find_values_from_key, find_values_containing_substring

def get_storage_cost(region_id, volume_type) :
    pricing = boto3.client('pricing', region_name='us-east-1')

    response = pricing.get_products(
        ServiceCode='AmazonS3',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Storage'},
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'volumeType', 'Value': volume_type},
        ],
        MaxResults=1
    )

    pricePerUnit = find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))
    pricePerUnit = sorted(pricePerUnit, key=lambda i:float(i['USD']))
    for i in range(0, len(pricePerUnit)):
        pricePerUnit[i]['USD'] = float(pricePerUnit[i]['USD'])
    unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    return unit, pricePerUnit


def get_cost(region_id, group_description) :
    pricing = boto3.client('pricing', region_name='us-east-1')

    response = pricing.get_products(
        ServiceCode='AmazonS3', 
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'API Request'},
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'groupDescription', 'Value': group_description},
        ],
        MaxResults=1
    )
    unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    pricePerUnit = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    return unit, pricePerUnit


def get_object_cost(region_id, feecode):
    pricing = boto3.client('pricing', region_name='us-east-1')

    response = pricing.get_products(
        ServiceCode='AmazonS3', 
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'feeCode', 'Value': feecode}
        ],
        MaxResults=1
    )
    unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    pricePerUnit = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    return unit, pricePerUnit


def get_other_cost(region_id, group_description):
    pricing = boto3.client('pricing', region_name='us-east-1')
    s3 = boto3.client('s3')

    response = pricing.get_products(
        ServiceCode='AmazonS3', 
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_id},
            {'Type': 'TERM_MATCH', 'Field': 'groupDescription', 'Value': group_description},
        ],
        MaxResults=1
    )

    unit = find_values_from_key('unit', json.loads(response['PriceList'][0]))[0]
    pricePerUnit = float(find_values_from_key('pricePerUnit', json.loads(response['PriceList'][0]))[0]['USD'])
    return unit, pricePerUnit


def get_standard_cost(region_id):
    storage = get_storage_cost(region_id, "Standard")
    pcpl_request = get_cost(region_id, "PUT/COPY/POST or LIST requests")
    others_request = get_cost(region_id, "GET and all other requests")
    data_returned = get_cost(region_id, "Data Returned by S3 Select in Standard")
    data_scanned = get_cost(region_id, "Data Scanned by S3 Select in Standard")

    amount_data = 2030.18780
    amount_pcpl_request = 3740740
    amount_others_request = 17248714
    amount_data_returned = 0.02255
    amount_data_scanned = 0.01311

    storage_cost = 0
    if amount_data <= 51200 :
        storage_cost = amount_data * storage[1][2]['USD']
    elif amount_data > 51200 and amount_data <= 512000 :
        storage_cost = (51200 *  storage[1][2]['USD']) + ((amount_data-51200) * storage[1][1]['USD'])
    elif amount_data > 512000 :
        storage_cost = (51200 * storage[1][2]['USD']) + (460800 * storage[1][1]['USD']) + \
            ((amount_data*-512000) * storage[1][0]['USD'])

    pcpl_request_cost = amount_pcpl_request * pcpl_request[1]
    others_request_cost = amount_others_request * others_request[1]
    data_returned_cost = amount_data_returned * data_returned[1]
    data_scanned_cost = amount_data_scanned * data_scanned[1]

    monthly_cost = storage_cost + pcpl_request_cost + others_request_cost + data_returned_cost + data_scanned_cost

    return monthly_cost, storage, pcpl_request, others_request, data_returned, data_scanned, storage_cost, \
        pcpl_request_cost, others_request_cost, data_returned_cost, data_scanned_cost


def get_standard_IA_cost(region_id):
    storage = get_storage_cost(region_id, 'Standard - Infrequent Access')
    pcpl_request = get_cost(region_id, "PUT/COPY/POST or LIST requests to Standard-Infrequent Access") # ini per 1.000 request
    others_request = get_cost(region_id, "GET and all other requests  to Standard-Infrequent Access") # ini per 10.000 get
    lifecycle_transition = get_other_cost(region_id, "Lifecycle Transition Requests into Standard-Infrequent Access")
    data_retrieval = get_cost(region_id, "Object Retrieval in Standard-Infrequent Access")
    data_returned = get_cost(region_id, "Data Returned by S3 Select in Standard-Infrequent Access") #ini per GB
    data_scanned = get_cost(region_id, "Data Scanned by S3 Select in Standard-Infrequent Access") #ini per GB

    amount_data = 100000
    amount_pcpl_request = 1000
    amount_others_request = 2000
    amount_lifecycle_transition = 3000
    amount_data_retievals = 4000
    amount_data_returned = 5000
    amount_data_scanned = 6000

    storage_cost = amount_data * storage[1][0]['USD']
    pcpl_request_cost = amount_pcpl_request * pcpl_request[1]
    others_request_cost = amount_others_request * others_request[1]
    lifecycle_transition_cost = amount_lifecycle_transition * lifecycle_transition[1]
    data_retrieval_cost = amount_data_retievals * data_retrieval[1]
    data_returned_cost = amount_data_returned * data_returned[1]
    data_scanned_cost = amount_data_scanned * data_scanned[1]

    monthly_cost = storage_cost + pcpl_request_cost + others_request_cost + lifecycle_transition_cost + data_retrieval_cost + \
        data_returned_cost + data_scanned_cost

    return monthly_cost, storage, pcpl_request, others_request, data_returned, data_scanned, storage_cost, \
        pcpl_request_cost, others_request_cost, data_returned_cost, data_scanned_cost, lifecycle_transition, \
        lifecycle_transition_cost, data_retrieval, data_retrieval_cost


def get_INT_cost(region_id):
    pcpl_request = get_other_cost(region_id, "PUT/COPY/POST or LIST requests to Intelligent-Tiering") # ini per 1.000 request
    others_request = get_other_cost(region_id, "GET and all other requests to Intelligent-Tiering") # ini per 10.000 get
    lifecycle_transition = get_other_cost(region_id, "Lifecycle Transition Requests into Intelligent-Tiering")
    data_returned = get_other_cost(region_id, "Data Returned by S3 Select in Intelligent-Tiering") #ini per GB
    data_scanned = get_other_cost(region_id, "Data Scanned by S3 Select in Intelligent-Tiering") #ini per GB

    # percentage storage
    monitoring_and_automation_object = get_object_cost(region_id, "S3-Monitoring and Automation-ObjectCount")
    frequent_access_tier = get_storage_cost(region_id, "Intelligent-Tiering Frequent Access")
    infrequent_access_tier = get_storage_cost(region_id, "Intelligent-Tiering Infrequent Access")
    archive_instant_access_tier = get_storage_cost(region_id, "Intelligent-Tiering Archive Instant Access")
    archive_access_tier = get_storage_cost(region_id, "IntelligentTieringArchiveAccess")
    deep_archive_access_tier = get_storage_cost(region_id, "IntelligentTieringDeepArchiveAccess")

    # its still dummy data
    amount_data = 100000 # in gb
    amount_pcpl_request = 1000
    amount_others_request = 2000
    amount_lifecycle_transition = 3000
    amount_data_returned = 4000
    amount_data_scanned = 5000
    average_object_size = 16 # in mb
    percentage_frequent_access_tier = 60/100
    percentage_infrequent_access_tier = 5/100
    percentage_archive_instant_access_tier = 5/100
    percentage_archive_access_tier = 10/100
    percentage_deep_archive_access_tier = 20/100


    pcpl_request_cost = amount_pcpl_request * pcpl_request[1]
    others_request_cost = amount_others_request * others_request[1]
    lifecycle_transition_cost = amount_lifecycle_transition * lifecycle_transition[1]
    data_returned_cost = amount_data_returned * data_returned[1]
    data_scanned_cost = amount_data_scanned * data_scanned[1]

    if percentage_frequent_access_tier + percentage_infrequent_access_tier + percentage_archive_instant_access_tier + \
        percentage_archive_access_tier + percentage_deep_archive_access_tier != 1 :
        return ParseError('invalid percentage')

    if amount_data <= 51200 :
        frequent_access_tier_cost = amount_data * percentage_frequent_access_tier * frequent_access_tier[1][2]['USD']
    elif amount_data > 51200 and amount_data <= 512000 :
        frequent_access_tier_cost = (51200 * frequent_access_tier[1][2]['USD']) + ((amount_data*percentage_frequent_access_tier-51200) * \
            frequent_access_tier[1][1]['USD'])
    elif amount_data > 512000 :
        frequent_access_tier_cost = (51200 * frequent_access_tier[1][2]['USD']) + (460800 * frequent_access_tier[1][1]['USD']) + \
            ((amount_data*percentage_frequent_access_tier-512000) * frequent_access_tier[1][0]['USD'])

    average_object_cost_in_gb = average_object_size *  0.0009765625
    monitoring_and_automation_object_cost = monitoring_and_automation_object[1] * round((amount_data / average_object_cost_in_gb), 1)
    infrequent_access_tier_cost = percentage_infrequent_access_tier * amount_data * infrequent_access_tier[1][0]['USD']
    archive_instant_access_tier_cost = percentage_archive_instant_access_tier * amount_data * archive_instant_access_tier[1][0]['USD']
    archive_access_tier_cost = percentage_archive_access_tier * amount_data * archive_access_tier[1][0]['USD']
    deep_archive_access_tier_cost = percentage_deep_archive_access_tier * amount_data * deep_archive_access_tier[1][0]['USD']

    storage_cost = frequent_access_tier_cost +  infrequent_access_tier_cost + archive_instant_access_tier_cost + \
        archive_access_tier_cost + deep_archive_access_tier_cost

    monthly_cost = pcpl_request_cost + others_request_cost + lifecycle_transition_cost + data_returned_cost + data_scanned_cost + \
        monitoring_and_automation_object_cost + storage_cost


    return monthly_cost, ("GB-Mo", ""), pcpl_request, others_request, data_returned, data_scanned, storage_cost, \
        pcpl_request_cost, others_request_cost, data_returned_cost, data_scanned_cost, lifecycle_transition, \
        lifecycle_transition_cost, monitoring_and_automation_object, monitoring_and_automation_object_cost


def get_storage_class(obj):
    region_id = find_region(obj)
    try :
        storage_class = find_values_from_key('storage_class', obj['planned_values']['root_module']['resources'])[0]
    except : 
        storage_class = 'STANDARD'
    # storage_class = "STANDARD_IA" # we can fill this variable for testing

    if storage_class == "STANDARD_IA" :
        value = get_standard_IA_cost(region_id)
    elif storage_class == "INTELLIGENT_TIERING":
        value = get_INT_cost(region_id)
    else :
        value = get_standard_cost(region_id)

    return value, storage_class


def calculate_s3(address_param, file_obj):

    s3_value = get_storage_class(file_obj)
    address = find_values_containing_substring("address", address_param, file_obj)[0]

    fields = [
        [' ', ' ', ' ', ' '],
        [address, ' ', ' ', ' '],
        [f'├── {s3_value[1]}', ' ', ' ', ' '],
        [f'├── Storage {s3_value[1]}', 'amount of storage (dummy)', f'{s3_value[0][1][0]}', f'${s3_value[0][6]:.5f}'],
        [f'├── PUT, COPY, POST, LIST requests', 'amount of PCPL request (dummy)', f'{s3_value[0][2][0]}', f'${s3_value[0][7]:.5f}'],
        [f'├── GET, SELECT, and all other requests', 'amount of others request (dummy)', f'{s3_value[0][3][0]}', f'${s3_value[0][8]:.5f}'],
        [f'├── Select data returned', 'amount of select data returned (dummy)', f'{s3_value[0][4][0]}', f'${s3_value[0][9]:.5f}'],
        [f'└── Select data scanned', 'amount of select data scanned (dummy)', f'{s3_value[0][5][0]}', f'${s3_value[0][10]:.5f}']
    ]

    if s3_value[1] == "STANDARD_IA":
        fields.append([f'├── Lifecycle Transition requests', 'amount of lifecycle transition request (dummy)', f'{s3_value[0][11][0]}', f'${s3_value[0][12]:.5f}'])
        fields.append([f'└── Data retrievals', 'amount of data retrievals(dummy)', f'{s3_value[0][13][0]}', f'${s3_value[0][14]:.5f}'])
    elif s3_value[1] == "INTELLIGENT_TIERING":
        fields.append([f'├── Lifecycle Transition requests', 'amount of lifecycle transition request (dummy)', f'{s3_value[0][11][0]}', f'${s3_value[0][12]:.5f}'])
        fields.append([f'└── Monitoring and Automation objects cost', 'amount of monitoring and automation object (dummy)', f'{s3_value[0][13][0]}', f'${s3_value[0][14]:.5f}'])

    fields_total = [f'└── Total', ' ', ' ', f'${s3_value[0][0]:.5f}']

    with open(r'/usr/local/bin/infra-cost-estimator/data/data.csv', 'a', encoding="utf-8") as f:
        writer = csv.writer(f)
        for i in range(0,len(fields)) :
            writer.writerow(fields[i])
        writer.writerow(fields_total)

    return float(s3_value[0][0])
