import os
import json

from analyzers.metrics_parsers import PARSERS
from analyzers.metrics_analyzer import MetricsAnalyzer
from analyzers.metrics_history import load_history
from config.settings import ENDPOINTS, SCENARIOS

def load_test_config(result_folder):
    config_file = os.path.join(result_folder, "test_config.json")

    if not os.path.exists(config_file):
        return None

    with open(config_file, "r", encoding="utf-8") as file:
        return json.load(file)

def load_script_config(config_path):
    if not os.path.exists(config_path):
        return None

    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)

def _resolve_target_description(target_type, target_name):
    if target_type == "endpoint":
        endpoint = ENDPOINTS.get(target_name, {})
        return endpoint.get("description", "")

    if target_type == "flow":
        scenario = SCENARIOS.get(target_name, {})
        return scenario.get("description", "")

    return ""

def _confirm_overwrite(message):
    while True:
        choice = input(f"\n{message} (type 'y' for yes, and 'n' for no): ").strip().lower()

        if choice == "y":
            return True

        if choice == "n":
            return False

        print("Invalid choice. You have to enter only 'y' or 'n'.")

def run_analysis(result_folder, tool, target_type, target_name, test_type, test_params, analyst_provider, analyst_model):
    parser = PARSERS.get(tool)

    if not parser:
        print(f"\nNo parser available for {tool}, analysis aborted.")
        return False

    metrics = parser(result_folder)

    if metrics is None:
        print("\nCould not parse metrics from the result folder, analysis aborted.")
        return False

    target_description = _resolve_target_description(target_type, target_name)

    analysis_file = os.path.join(result_folder, f"analysis_{analyst_provider}.md")

    if os.path.exists(analysis_file):
        should_overwrite = _confirm_overwrite(f"Analysis from {analyst_provider} already exists for this test. Overwrite?")

        if not should_overwrite:
            return False

    history = load_history(target_type, target_name, test_type)

    analyzer = MetricsAnalyzer(provider=analyst_provider, model=analyst_model)

    print("\nCalling the model for analysis...")

    report = analyzer.analyze(target_type=target_type, target_name=target_name, target_description=target_description, test_type=test_type, test_params=test_params, tool=tool, metrics=metrics, history=history)

    print("\n" + "=" * 70)
    print("Analysis report:")
    print("=" * 70)
    print(report)
    print("=" * 70)

    saved_path = analyzer.save_report(report, result_folder)
    print(f"\nReport saved to: {saved_path}")

    return True