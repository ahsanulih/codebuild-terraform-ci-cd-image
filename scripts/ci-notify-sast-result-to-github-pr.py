#!/usr/bin/env python3
# Notify Plan Artifact to Github Pull Request

import os
import sys

from jinja2 import Environment, FileSystemLoader

import notify_github as gh
from contextlib import contextmanager


@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


if not os.path.isfile(os.getenv('TF_WORKING_DIR', "")+"/terraform.tfplan"):
    print("terraform.tfplan not found. Skipping this step")
    sys.exit(0)

# we need to change working directory so tfenv can get terraform version
# from terraform configuration or .terraform-version file
with cwd(os.getenv('TF_WORKING_DIR')):
    command = os.popen('terraform show terraform.tfplan -no-color')
    tf_plan = command.read()
    command.close()

f = open("artifact/metadata.json", "r")
metadata = f.read()

if not os.path.isfile(os.getenv('TF_WORKING_DIR', "")+"/sast-result-summary"):
    print("sast-result-summary not found. Skipping this step")
elif not os.path.isfile(os.getenv('TF_WORKING_DIR', "")+"/sast-result-detail"):
    print("sast-result-detail not found. Skipping this step")
else:
    with cwd(os.getenv('TF_WORKING_DIR')):
        command_sast_result_summary = os.popen('cat sast-result-summary')
        sast_result_summary = command_sast_result_summary.read()
        command_sast_result_summary.close()

        command_sast_result_detail = os.popen('cat sast-result-detail')
        sast_result_detail = command_sast_result_detail.read()
        command_sast_result_detail.close()
    template = Environment(
        loader=FileSystemLoader(os.path.dirname(os.path.realpath(__file__)) + "/templates")
    ).get_template("terraform_output_with_sast.j2")
    message = template.render(
        metadata_json=metadata,
        file_name="terraform.tfplan",
        sast_result_summary_file_name="sast-result-summary",
        sast_result_summary_output=sast_result_summary,
        terraform_output=tf_plan,
        sast_result_detail_file_name="sast-result-detail",
        sast_result_detail_output=sast_result_detail
    )
    gh.send_pr_comment(payload=message)
    