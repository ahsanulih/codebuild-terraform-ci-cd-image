#!/bin/bash
result=${PWD##*/}          # to assign current directory name to a variable
result=${result:-/}        # to correct for the case where PWD=/

terraform plan -out "$result"-plan 
terraform show -json "$result"-plan > "$result"-plan.json
cat /usr/local/bin/"$result"-plan.json
pwd
ls -la

if [ "${result: -3}" = "app" ]
then
  printf "%s\n" "------------------------------------------------------------------------" > infra_cost_result
  printf "%s\n" "This is a stack module directory" >> infra_cost_result
  printf "%s\n" "------------------------------------------------------------------------" >> infra_cost_result
  python3 /usr/local/bin/infra_cost_find_cost_asg.py "$result"-plan.json >> infra_cost_result
  python3 /usr/local/bin/infra_cost_find_cost_alb.py "$result"-plan.json >> infra_cost_result
elif [ "${result: -8}" = "postgres" ]
then
  printf "%s\n" "------------------------------------------------------------------------" > infra_cost_result
  printf "%s\n" "This is a postgres directory" >> infra_cost_result
  printf "%s\n" "------------------------------------------------------------------------" >> infra_cost_result
  python3 /usr/local/bin/infra_cost_find_cost_rds.py "$result"-plan.json >> infra_cost_result
fi

ls -la
cat infra_cost_result