"""Function to find AWS region id and region name"""

import json
from find_values import find_values_from_key

with open("/usr/local/bin/infra-cost-estimator/data/region-id-to-region-name.json", encoding="utf-8") as file:
    region_id_to_name_obj = json.load(file)


def find_region(obj):
    """
    Function to find AWS region.
    Receive 1 terraform plan JSON object as parameter.
    Return region id and region name. Example: "ap-southeast-1", "Asia Pacific (Singapore)"
    """
    try:
        region_id = find_values_from_key('region', obj['prior_state'])[0]
    except:
        region_id = obj['configuration']['provider_config']['aws'][
            'expressions']['region']['constant_value']

    region_name = region_id_to_name_obj[region_id]
    return region_id, region_name
