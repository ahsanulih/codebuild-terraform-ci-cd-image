"""Function to find AWS region"""

import json

with open("/usr/local/bin/region-id-to-name.json", encoding="utf-8") as file:
    region_id_to_name_obj = json.load(file)

def find_region(obj):
    """
    Function to find AWS region.
    Receive 1 terraform plan JSON object as parameter.
    Return region name. Example: "Asia Pacific (Singapore)"
    """
    region_id = obj['configuration']['provider_config']['aws'][
        'expressions']['region']['constant_value']
    region_name = region_id_to_name_obj[region_id]
    return region_name
    