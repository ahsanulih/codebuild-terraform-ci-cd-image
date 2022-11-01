#!/bin/bash
result=${PWD##*/}   # to assign current directory name to a variable
result=${result:-/} # to correct for the case where PWD=/

FILE="$result"-plan.json
if [ ! -s "$FILE" ]; then
    terraform plan -out "$result"-plan
    terraform show -json "$result"-plan >"$result"-plan.json
fi

python3 /usr/local/bin/infra-cost-estimator/scripts/main.py "$result"-plan.json >>aws-resource-charges-estimations

if [ $? -eq 0 ]; then
    echo -e "\nSuccessfully executed infra cost estimator scripts"
    exit 0
else
    echo -e "\nCould not execute infra cost estimator scripts" >&2
    exit 0
fi
