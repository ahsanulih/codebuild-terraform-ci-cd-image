"""Print data.csv"""

import pandas as pd
from tabulate import tabulate

data = pd.read_csv('/usr/local/bin/infra-cost-estimator/data/data.csv')
df_headers = ["Name", "Monthly Qty", "Unit", "Monthly Cost"]

print(tabulate(data, headers=df_headers, tablefmt='simple', showindex=False))
