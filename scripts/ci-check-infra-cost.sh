#!/bin/bash
result=${PWD##*/}   # to assign current directory name to a variable
result=${result:-/} # to correct for the case where PWD=/

FILE="$result"-plan.json
if [ ! -s "$FILE" ]; then
    terraform plan -out "$result"-plan
    terraform show -json "$result"-plan >"$result"-plan.json
fi

python3 /usr/local/bin/infra-cost-estimator/scripts/main.py "$result"-plan.json >>infra_cost_estimation
