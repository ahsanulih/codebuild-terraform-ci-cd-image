#!/bin/bash -x
result=${PWD##*/}   # to assign current directory name to a variable
result=${result:-/} # to correct for the case where PWD=/

echo "checkov --version"
checkov --version

echo "Working dir : $TF_WORKING_DIR"
if [ "$TF_WORKING_DIR" != "" ]; then
    cd $TF_WORKING_DIR
    FILE="$result"-plan.json
    if [ ! -s "$FILE" ]; then
        terraform plan -out "$result"-plan
        terraform show -json "$result"-plan >"$result"-plan.json
    fi
fi

echo "# SUMMARY"
cmd="python checkov/failed_summarizer.py -d ."
echo "# DETAIL"
cmd="checkov -d."

checkov -f "$result"-plan.json >>sast-result

if [ $? -eq 0 ]; then
    echo -e "\nSuccessfully executed static app security test using Checkov"
    exit 0
else
    echo -e "\nCould not execute static app security test using Checkov" >&2
    exit 0
fi
