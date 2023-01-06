"""Function to find operating system from AMI platform"""

import json

with open("/usr/local/bin/infra-cost-estimator/data/platform-to-operating-system.json", encoding="utf-8") as file:
    platform_to_operating_system_obj = json.load(file)


def find_operating_system(platform_details):
    """
    Function to find operating system from AMI platform"
    """
    operating_system = platform_to_operating_system_obj[platform_details]
    return operating_system
