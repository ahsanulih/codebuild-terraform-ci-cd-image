#!/bin/bash
result=${PWD##*/}   # to assign current directory name to a variable
result=${result:-/} # to correct for the case where PWD=/

echo "Working dir : $TF_WORKING_DIR"
if [ "$TF_WORKING_DIR" != "" ]; then
    cd $TF_WORKING_DIR
fi

echo "checkov --version"
checkov --version

echo "#EXECUTING CHECKOV SUMMARIZED TEST"
python3 /usr/local/bin/checkov-scripts/failed_summarizer.py -d $(pwd) --skip-check CKV_AWS_23 >>sast-result-summary

if [ $? -eq 0 ]; then
    echo -e "\nSuccessfully executed summarized static app security test using Checkov"
else
    echo -e "\nThere were some failed checks during summarized static app security test using Checkov" >&2
fi

echo "#EXECUTING CHECKOV DETAILED TEST"
checkov -d . --skip-check CKV_AWS_23 >>sast-result-detail

if [ $? -eq 0 ]; then
    echo -e "\nSuccessfully executed detailed static app security test using Checkov"
    exit 0
else
    echo -e "\nThere were some failed checks during detailed static app security test using Checkov" >&2
    exit 0
fi
