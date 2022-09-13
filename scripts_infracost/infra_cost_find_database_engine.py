"""Function to find database engine from Terraform plan result"""

import json

with open("/usr/local/bin/database-engine.json", encoding="utf-8") as file:
    database_engine_obj = json.load(file)

def find_engine(engine):
    """
    Function to find database engine from engine
    """
    database_engine = database_engine_obj[engine]
    return database_engine
