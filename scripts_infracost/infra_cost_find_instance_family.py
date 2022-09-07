"""Function to find instance family from instance type"""

import json

with open("instance-type-to-instance-family.json", encoding="utf-8") as file:
    instance_type_to_instance_family_obj = json.load(file)

def find_instance_family(instance_type):
    """
    Function to find instance family from instance type
    """
    instance_family = instance_type_to_instance_family_obj[instance_type[0]]
    return instance_family
