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

if not os.path.isfile(os.getenv('TF_WORKING_DIR', "")+"/aws-resource-charges-estimations"):
    print("aws-resource-charges-estimations not found. Skipping this step")
else:
    with cwd(os.getenv('TF_WORKING_DIR')):
        command_infracost = os.popen('cat aws-resource-charges-estimations')
        aws_resource_charges_estimations = command_infracost.read()
        command.close()
    template = Environment(
        loader=FileSystemLoader(os.path.dirname(os.path.realpath(__file__)) + "/templates")
    ).get_template("terraform_output_with_infra_cost.j2")
    message = template.render(
        metadata_json=metadata,
        file_name="terraform.tfplan",
        infra_cost_file_name="aws-resource-charges-estimations",
        terraform_output=tf_plan,
        infra_cost_output=aws_resource_charges_estimations
    )
    gh.send_pr_comment(payload=message)
