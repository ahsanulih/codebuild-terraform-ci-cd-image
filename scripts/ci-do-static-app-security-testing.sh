#!/bin/bash
CHECKOV_SKIP_CHECK="CKV_AWS_23,CKV_AWS_144,CKV2_AWS_62,CKV2_AWS_5"

echo "Working dir : $TF_WORKING_DIR"
if [ "$TF_WORKING_DIR" != "" ]; then
    cd $TF_WORKING_DIR
fi

echo "checkov --version"
checkov --version

echo "#EXECUTING CHECKOV SUMMARIZED TEST"
python3 /usr/local/bin/checkov-scripts/summarizer.py -d $(pwd) --skip-check ${CHECKOV_SKIP_CHECK} >>sast-result-summary

if [ $? -eq 0 ]; then
    echo -e "\nSuccessfully executed summarized static app security test using Checkov"
else
    echo -e "\nThere were some failed checks during summarized static app security test using Checkov" >&2
fi

echo "#EXECUTING CHECKOV DETAILED TEST"
checkov -d . --skip-check ${CHECKOV_SKIP_CHECK} --quiet >>sast-result-detail

if [ $? -eq 0 ]; then
    echo -e "\nSuccessfully executed detailed static app security test using Checkov"
    exit 0
else
    echo -e "\nThere were some failed checks during detailed static app security test using Checkov" >&2
    exit 0
fi
