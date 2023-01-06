import json
import sys

from display_cost_estimation import display_cost_estimation
from find_cost_alb import calculate_alb_and_lcu
from find_cost_asg import calculate_asg_and_ebs
from find_cost_cw_log_group import calculate_cwl
from find_cost_ec2 import calculate_ec2_and_ebs
from find_cost_rds import calculate_rds
from find_cost_sqs import calculate_sqs
from find_cost_s3 import calculate_s3
from find_values import find_values_from_key

class InfracostEstimator(object):
    def __init__(self):
        self.not_free_resource_counter = 0
        self.free_resource_counter = 0
        self.not_supported_resource_counter = 0
        self.total_cost = 0
        self.not_free_resource_set = {
            "aws_lb",
            "aws_cloudwatch_log_group",
            "aws_db_instance",
            "aws_instance",
            "aws_autoscaling_group",
            # "aws_s3_bucket",
            "aws_sqs_queue"
        }
        self.free_resource_hashmap = {
            "aws_acm_certificate": 0,
            "aws_acm_certificate_validation": 0,
            "aws_cloudwatch_event_rule": 0,
            "aws_cloudwatch_event_target": 0,
            "aws_codebuild_webhook": 0,
            "aws_db_parameter_group": 0,
            "aws_eip": 0,
            "aws_iam_instance_profile": 0,
            "aws_iam_policy_document": 0,
            "aws_iam_role": 0,
            "aws_iam_role_policy": 0,
            "aws_iam_role_policy_attachment": 0,
            "aws_lambda_permission": 0,
            "aws_launch_template": 0,
            "aws_lb_listener": 0,
            "aws_lb_listener_rule": 0,
            "aws_lb_target_group": 0,
            "aws_lb_target_group_attachment": 0,
            "aws_s3_bucket_public_access_block": 0,
            "aws_security_group": 0,
            "aws_security_group_rule": 0,
            "aws_ssm_parameter": 0,
            "aws_subnet": 0,
            "aws_vpc": 0,
            "random_id": 0
        }
        self.not_supported_resource_hashmap = {}


    def calculate_cost(self, tf_resource, tf_plan):
        if tf_resource["type"] == "aws_autoscaling_group":
            self.not_free_resource_counter += 1
            self.total_cost += calculate_asg_and_ebs(tf_resource["address"], tf_plan)
        if tf_resource["type"] == "aws_cloudwatch_log_group":
            self.not_free_resource_counter += 1
            self.total_cost += calculate_cwl(tf_resource["address"], tf_plan)
        if tf_resource["type"] == "aws_db_instance":
            self.not_free_resource_counter += 1
            self.total_cost += calculate_rds(tf_resource["address"], tf_plan)
        if tf_resource["type"] == "aws_instance":
            self.not_free_resource_counter += 1
            self.total_cost += calculate_ec2_and_ebs(tf_resource["address"], tf_plan)
        if tf_resource["type"] == "aws_lb":
            self.not_free_resource_counter += 1
            self.total_cost += calculate_alb_and_lcu(tf_resource["address"], tf_plan)
        if tf_resource["type"] == "aws_s3_bucket":
            self.not_free_resource_counter += 1
            self.total_cost += calculate_s3(tf_resource["address"], tf_plan)
        if tf_resource["type"] == "aws_sqs_queue":
            self.not_free_resource_counter += 1
            self.total_cost += calculate_sqs(tf_resource["address"], tf_plan)
        

    def main(self, tf_plan_file):
        with open(f"{tf_plan_file}", encoding="utf-8") as file:
            tf_plan_obj = json.load(file)

        try:
            root_module_resources_obj = tf_plan_obj["planned_values"]["root_module"]["resources"]
        except:
            root_module_resources_obj = {}
            
        try:
            child_module_resources_obj = tf_plan_obj["planned_values"]["root_module"]["child_modules"]
        except:
            child_module_resources_obj = {}

        for resource in root_module_resources_obj:
            if resource["mode"] == "data":
                continue
            if resource["type"] in self.free_resource_hashmap:
                self.free_resource_counter += 1
                self.free_resource_hashmap[resource["type"]] += 1
            elif resource["type"] in self.not_free_resource_set:
                self.calculate_cost(resource, tf_plan_obj)
            else:
                self.not_supported_resource_counter += 1
                if resource["type"] not in self.not_supported_resource_hashmap:
                    self.not_supported_resource_hashmap[resource["type"]] = 1
                else:
                    self.not_supported_resource_hashmap[resource["type"]] += 1

        child_module_resources = find_values_from_key("resources", child_module_resources_obj)
        for resources in child_module_resources:
            for resource in resources:
                if resource["mode"] == "data":
                    continue
                if resource["type"] in self.free_resource_hashmap:
                    self.free_resource_counter += 1
                    self.free_resource_hashmap[resource["type"]] += 1
                elif resource["type"] in self.not_free_resource_set:
                    self.calculate_cost(resource, tf_plan_obj)
                else:
                    self.not_supported_resource_counter += 1
                    if resource["type"] not in self.not_supported_resource_hashmap:
                        self.not_supported_resource_hashmap[resource["type"]] = 1
                    else:
                        self.not_supported_resource_hashmap[resource["type"]] += 1

if __name__ == "__main__":
    ic = InfracostEstimator()
    ic.main(sys.argv[1])
    display_cost_estimation(ic.not_free_resource_counter, ic.free_resource_counter, ic.not_supported_resource_counter,
                            ic.free_resource_hashmap, ic.not_supported_resource_hashmap, ic.total_cost)
