"""Display cost estimation"""

import pandas as pd
from tabulate import tabulate


def display_cost_estimation(not_free_resource_counter, free_resource_counter, not_supported_resource_counter,
                            free_resource_hashmap, not_supported_resource_hashmap, total_cost):
    """
    Function to display cost estimation from data.csv
    """
    data = pd.read_csv('/usr/local/bin/infra-cost-estimator/data/data.csv')
    df_headers = ["Name", "Monthly Qty", "Unit", "Monthly Cost"]
    if not_free_resource_counter > 0:
        print(tabulate(data, headers=df_headers, tablefmt='simple', showindex=False))

    print("\nSUMMARY")
    print("──────────────────────────────")

    if not_free_resource_counter == 0 and free_resource_counter == 0 and not_supported_resource_counter == 0:
        print("No resource detected")
    elif not_free_resource_counter + free_resource_counter + not_supported_resource_counter == 1:
        print("1 resource was detected:")

    else:
        print(f"{not_free_resource_counter + free_resource_counter + not_supported_resource_counter} resources were detected:")
        if not_free_resource_counter == 1:
            print(f"∙ {not_free_resource_counter} was estimated with total monthly cost: ${total_cost:.2f}")
        elif not_free_resource_counter > 1:
            print(f"∙ {not_free_resource_counter} were estimated with total monthly cost: ${total_cost:.2f}")

        if free_resource_counter == 1:
            print(f"∙ {free_resource_counter} was free")
        elif free_resource_counter > 1:
            print(f"∙ {free_resource_counter} were free")
        for key, value in free_resource_hashmap.items():
            if value != 0:
                print(f"    ∙ {value} x {key}")

        if not_supported_resource_counter == 1:
            print(f"∙ {not_supported_resource_counter} is not supported yet")
        elif not_supported_resource_counter > 1:
            print(f"∙ {not_supported_resource_counter} are not supported yet")
        for key, value in not_supported_resource_hashmap.items():
            if value != 0:
                print(f"    ∙ {value} x {key}")
