#!/bin/bash
result=${PWD##*/}   # to assign current directory name to a variable
result=${result:-/} # to correct for the case where PWD=/

echo "checkov --version"
checkov --version

echo "#EXECUTING CHECKOV SUMMARIZED TEST"
python3 checkov-scripts/failed_summarizer.py -d $(pwd) >>sast-result-summary

echo "Working dir : $TF_WORKING_DIR"
if [ "$TF_WORKING_DIR" != "" ]; then
    cd $TF_WORKING_DIR
    FILE="$result"-plan.json
    if [ ! -s "$FILE" ]; then
        terraform plan -out "$result"-plan
        terraform show -json "$result"-plan >"$result"-plan.json
    fi
fi

echo "#EXECUTING CHECKOV DETAILED TEST"
checkov -f "$result"-plan.json >>sast-result-detail

if [ $? -eq 0 ]; then
    echo -e "\nSuccessfully executed static app security test using Checkov"
    exit 0
else
    echo -e "\nThere were some failed checks during static app security test using Checkov" >&2
    exit 0
fi
