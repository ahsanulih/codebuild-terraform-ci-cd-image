"""Function to find AWS region id"""

from find_values import find_values_from_key


def find_region(obj):
    """
    Function to find AWS region id.
    Receive 1 terraform plan JSON object as parameter.
    Return region id. Example: "ap-southeast-1"
    """
    try:
        region_id = find_values_from_key('region', obj['prior_state'])[0]
    except:
        try:
            region_id = obj['configuration']['provider_config']['aws']['expressions']['region']['constant_value']
        except:
            region_id = "ap-southeast-1"

    return region_id
