import os
import shutil
import subprocess
import json
import sys
import re
import glob
from datetime import datetime
from dotenv import load_dotenv

from config.settings import BASE_URL
from utils.paths import get_project_root

load_dotenv()

GATLING_PROJECT_PATH = os.getenv("GATLING_PROJECT_PATH")
JMETER_COMMAND = os.getenv("JMETER_COMMAND")

def convert_time_to_seconds(time_value):
    match = re.match(r"^(\d+)(s|m|h)$", time_value.strip())

    if not match:
        return 1

    number = int(match.group(1))
    unit = match.group(2)

    if unit == "s":
        return number

    if unit == "m":
        return number * 60

    if unit == "h":
        return number * 3600

    return 1

def calculate_spawn_rate(virtual_users, ramp_up):
    ramp_up_seconds = convert_time_to_seconds(ramp_up)

    if ramp_up_seconds <= 0:
        return virtual_users

    spawn_rate = virtual_users/ramp_up_seconds

    if spawn_rate < 1:
        return 1

    return round(spawn_rate, 2)

def create_temp_result_folder(provider_key, tool, target_type, target_name, test_type, test_params):
    project_root = get_project_root()

    folder_name = f"{target_type}_{target_name}_{test_type}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    result_folder = os.path.join(project_root, "_temp_results", provider_key, tool, f"{folder_name}_{timestamp}")

    os.makedirs(result_folder, exist_ok=True)

    save_test_config(result_folder, target_type, target_name, test_type, test_params)

    return result_folder

def save_test_config(result_folder, target_type, target_name, test_type, test_params):
    config = {"target_type": target_type, "target_name": target_name, "test_type": test_type,
        "test_params": {"virtual_users": test_params.get("virtual_users"), "duration": test_params.get("duration"), "ramp_up": test_params.get("ramp_up")}
    }

    config_file = os.path.join(result_folder, "test_config.json")

    with open(config_file, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=2, ensure_ascii=False)

def save_result_folder(temp_result_folder, provider_key, tool):
    project_root = get_project_root()

    final_folder = temp_result_folder.replace(os.path.join(project_root, "_temp_results"),os.path.join(project_root, "results"))

    os.makedirs(os.path.dirname(final_folder), exist_ok=True)

    if os.path.exists(final_folder):
        shutil.rmtree(final_folder)

    shutil.move(temp_result_folder, final_folder)

    return final_folder

def delete_result_folder(result_folder):
    if os.path.exists(result_folder):
        shutil.rmtree(result_folder)

def extract_java_class_name(script_path):
    with open(script_path, "r", encoding="utf-8") as file:
        code = file.read()

    match = re.search(r"public\s+class\s+(\w+)\s+extends\s+Simulation", code)

    if match:
        return match.group(1)

    return None

def run_locust_test(script_path, test_params, provider_key, target_type, target_name, test_type):
    result_folder = create_temp_result_folder(provider_key, "locust", target_type, target_name, test_type, test_params)

    virtual_users = test_params["virtual_users"]
    duration = test_params["duration"]
    ramp_up = test_params["ramp_up"]
    spawn_rate = calculate_spawn_rate(virtual_users, ramp_up)

    csv_prefix = os.path.join(result_folder, "locust_result")
    html_report = os.path.join(result_folder, "locust_report.html")
    output_file = os.path.join(result_folder, "run_output.txt")

    command = [sys.executable, "-m", "locust", "-f", script_path, "--headless", "--host", BASE_URL, "--users", str(virtual_users), "--spawn-rate", str(spawn_rate), "--run-time", duration, "--csv", csv_prefix, "--html", html_report]

    print("Command:")
    print(" ".join(command))

    with open(output_file, "w", encoding="utf-8") as file:
        process = subprocess.run(command, stdout=file, stderr=subprocess.STDOUT, text=True)

    print("\nLocust test finished.")
    print(f"Temporary result folder: {result_folder}")

    if process.returncode != 0:
        print("Locust finished with errors. Check run_output.txt.")

    return result_folder

def run_k6_test(script_path, test_params, provider_key, target_type, target_name, test_type):
    result_folder = create_temp_result_folder(provider_key, "k6", target_type, target_name, test_type, test_params)

    summary_file = os.path.join(result_folder, "k6_summary.json")
    output_file = os.path.join(result_folder, "run_output.txt")

    command = ["k6", "run", script_path, "--summary-export", summary_file, "--summary-trend-stats", "avg,min,med,max,p(90),p(95),p(99)"]

    print("Command:")
    print(" ".join(command))

    with open(output_file, "w", encoding="utf-8") as file:
        process = subprocess.run(command, stdout=file, stderr=subprocess.STDOUT, text=True)

    print("\nk6 test finished.")
    print(f"Temporary result folder: {result_folder}")

    if process.returncode != 0:
        print("k6 finished with errors. Check run_output.txt.")

    return result_folder

def run_gatling_test(script_path, test_params, provider_key, target_type, target_name, test_type):
    result_folder = create_temp_result_folder(provider_key, "gatling", target_type, target_name, test_type, test_params)

    class_name = extract_java_class_name(script_path)

    if not class_name:
        print("Could not find public Gatling Simulation class name.")
        return result_folder

    simulations_folder = os.path.join(GATLING_PROJECT_PATH, "src", "test", "java")
    os.makedirs(simulations_folder, exist_ok=True)

    target_java_file = os.path.join(simulations_folder, f"{class_name}.java")
    shutil.copyfile(script_path, target_java_file)
    output_file = os.path.join(result_folder, "run_output.txt")

    command = [os.path.join(GATLING_PROJECT_PATH, "mvnw.cmd"), "gatling:test", f"-Dgatling.simulationClass={class_name}"]

    print("Command:")
    print(" ".join(command))

    with open(output_file, "w", encoding="utf-8") as file:
        process = subprocess.run(command, cwd=GATLING_PROJECT_PATH, stdout=file, stderr=subprocess.STDOUT, text=True)

    gatling_reports_folder = os.path.join(GATLING_PROJECT_PATH, "target", "gatling")

    if os.path.exists(gatling_reports_folder):
        report_folders = [
            folder for folder in glob.glob(os.path.join(gatling_reports_folder, "*"))
            if os.path.isdir(folder)
        ]

        if report_folders:
            latest_report = max(report_folders, key=os.path.getmtime)
            copied_report = os.path.join(result_folder, "gatling_report")
            shutil.copytree(latest_report, copied_report, dirs_exist_ok=True)

    print("\nGatling test finished.")
    print(f"Temporary result folder: {result_folder}")

    if process.returncode != 0:
        print("Gatling finished with errors. Check run_output.txt.")

    return result_folder

def run_jmeter_test(script_path, test_params, provider_key, target_type, target_name, test_type):
    result_folder = create_temp_result_folder(provider_key, "jmeter", target_type, target_name, test_type, test_params)

    result_file = os.path.join(result_folder, "jmeter_result.jtl")
    html_report_folder = os.path.join(result_folder, "html_report")
    output_file = os.path.join(result_folder, "run_output.txt")

    command = ["cmd", "/c", JMETER_COMMAND, "-n", "-t", script_path, "-l", result_file, "-e", "-o", html_report_folder]

    print("Command:")
    print(" ".join(command))

    with open(output_file, "w", encoding="utf-8") as file:
        process = subprocess.run(command, stdout=file, stderr=subprocess.STDOUT, text=True)

    print("\nJMeter test finished.")
    print(f"Temporary result folder: {result_folder}")

    if process.returncode != 0:
        print("JMeter finished with errors. Check run_output.txt.")

    return result_folder

RUNNERS = {"locust": run_locust_test, "k6": run_k6_test, "jmeter": run_jmeter_test, "gatling": run_gatling_test}