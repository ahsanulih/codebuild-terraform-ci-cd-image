import click
import os
import json
import subprocess
from tabulate import tabulate


def create_failed_summary_single_directory(
    dir_path:str,
    base_dir:str="../../..",
    skip_check:str=None,
) -> dict:
    target_dir = os.path.join(base_dir, dir_path)

    cmd = [
        "checkov",
        "-d", target_dir,
        "-o", "json"
    ]

    if skip_check:
        cmd = cmd + ["--skip-check", skip_check]

    output = subprocess.run(cmd, capture_output=True)
    stdout = json.loads(output.stdout)

    # handling single & multiple checks (terraform, security, etc)
    if type(stdout) != list:
        stdout = [stdout]

    # all checks passed somehow returns either:
    # - empty list: []
    # - dict without "results": {'passed': 0, ..}
    if (not stdout) or (not stdout[0].get("results")):
        output = subprocess.run(["checkov", "-v"], capture_output=True)
        temp = {}
        temp["terraform"] = {  # default to terraform
            "path": target_dir,
            "statistic": [],
            "total_failed": 0,
            "total_parsing_error": 0,
            "checkov_version": output.stdout.decode("utf-8")[:-1]
        }
        return temp

    result = {}
    for s in stdout:
        passed_counter = {}
        failed_counter = {}
        stats = []
                
        for f in s["results"]["failed_checks"]:
            cid = f["check_id"]
            if failed_counter.get(cid) == None:
                failed_counter[cid] = {}
                failed_counter[cid]["description"] = f["check_name"]
                failed_counter[cid]["count"] = 1
            else:
                failed_counter[cid]["count"] += 1

        failed_sorted_keys = sorted(
            failed_counter.keys(),
            key=lambda x:failed_counter[x]["count"],
            reverse=True
        )  # sort by the biggest count
        
        for k in failed_sorted_keys:
            stats.append({
                "Check": k,
                "Description": failed_counter[k]["description"],
                "Status": "Failed",
                "Count": failed_counter[k]["count"]
            })
            
        for f in s["results"]["passed_checks"]:
            cid = f["check_id"]
            if passed_counter.get(cid) == None:
                passed_counter[cid] = {}
                passed_counter[cid]["description"] = f["check_name"]
                passed_counter[cid]["count"] = 1
            else:
                passed_counter[cid]["count"] += 1
        
        passed_sorted_keys = sorted(
            passed_counter.keys(),
            key=lambda x:passed_counter[x]["count"],
            reverse=True
        )  # sort by the biggest count
        
        for k in passed_sorted_keys:
            stats.append({
                "Check": k,
                "Description": passed_counter[k]["description"],
                "Status": "Passed",
                "Count": passed_counter[k]["count"]
            })

        check_type = s.get("check_type", "terraform")
        result[check_type] = {
            "path": target_dir,
            "statistic": stats,
            "total_passed": s["summary"]["passed"],
            "total_failed": s["summary"]["failed"],
            "total_parsing_error": s["summary"]["parsing_errors"],
            "checkov_version": s["summary"]["checkov_version"]
        }

    return result


def pretty_print(failed_summary:list, format_type:str=json) -> None:
    if format_type == "json":
        print(json.dumps(failed_summary, indent=4))
    elif format_type == "text":
        temp = failed_summary[0]
        print(f"Checkov Version  : {temp[next(iter(temp))]['checkov_version']}")  # sampling from #1 element
        print(f"Checkov Policies : https://www.checkov.io/5.Policy%20Index/terraform.html")
        for fs in failed_summary:
            for k in fs.keys():
                print(f"\nCheck Type   : `{k}`")
                # print(f"Path         : {fs[k]['path']}")
                print(f":white_check_mark: Passed  : {fs[k]['total_passed']}")
                print(f":x: Failed : {fs[k]['total_failed']}")
                if fs[k].get("statistic"):
                    print(" ")
                    print(
                        tabulate(
                            [x.values() for x in fs[k]["statistic"]],
                            headers=fs[k]["statistic"][0].keys(),
                            tablefmt="github"
                        )
                    )
                else:
                    # empty fs["statistic"] means `All Passed` ^^
                    print("Statistic    : [All Passed]")

                err_count = fs[k]['total_parsing_error']
                if err_count != 0:
                    message = f"WARNING!!! Total Parsing Error : {err_count}"
                    print(f"\033[91m{message}\033[0m")  # colorize red
    else:
        raise Exception(f"Can't print! Invalid format_type: `{type}`")


@click.command()
@click.option('--directory', '-d', multiple=True,
    help='Target directory to check, can use multiple options'
)
@click.option('--base-dir', default="../../..", help='Base directory')
@click.option('--format', default="text", help='Output format (json/text)')
@click.option('--skip-check',
    help='Filter scan to run on all check but a specific check identifier'
)
def main(directory, base_dir, format, skip_check):
    """
    # Checkov failed check summarizer script\n
    Failed check_id sorted from the biggest count
    """
    summary = []

    for d in directory:
        summary.append(
            create_failed_summary_single_directory(d, base_dir, skip_check)
        )

    pretty_print(summary, format)


if __name__ == "__main__":
    main()
