import json
import os
from datetime import datetime

from analyzers.metrics_parsers import PARSERS
from utils.paths import get_project_root

def _build_group_key(target_type, target_name, test_type):
    return f"{target_type}_{target_name}_{test_type}"

def _get_history_file(group_key):
    project_root = get_project_root()
    history_folder = os.path.join(project_root, "metrics_history", group_key)
    os.makedirs(history_folder, exist_ok=True)
    return os.path.join(history_folder, "history.json")

def _load_history_records(history_file):
    if not os.path.exists(history_file):
        return []

    with open(history_file, "r", encoding="utf-8") as file:
        return json.load(file)

def _write_history_records(history_file, records):
    with open(history_file, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

def _build_history_record(provider_key, tool, target_type, target_name, test_type, test_params, metrics, result_folder):
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tool": tool,
        "provider": provider_key,
        "target_type": target_type,
        "target_name": target_name,
        "test_type": test_type,
        "load_parameters": {"virtual_users": test_params.get("virtual_users"), "duration": test_params.get("duration"), "ramp_up": test_params.get("ramp_up")},
        "metrics": metrics,
        "result_folder": result_folder
    }

def save_to_history(provider_key, tool, target_type, target_name, test_type, test_params, result_folder):
    parser = PARSERS.get(tool)

    if not parser:
        message = f"Parser for {tool} was not found. Metrics history was not updated."
        return False, message

    metrics = parser(result_folder)

    if metrics is None:
        message = "No metrics could be parsed, history not updated."
        return False, message

    aggregated = metrics.get("aggregated", {})
    total_requests = aggregated.get("total_requests", 0)
    error_rate = aggregated.get("error_rate_percent", 0)

    if total_requests == 0:
        message = "Test produced no requests, metrics not added to history."
        return False, message

    if error_rate >= 100:
        message = "Test failed completely, metrics not added to history."
        return False, message

    group_key = _build_group_key(target_type, target_name, test_type)
    history_file = _get_history_file(group_key)

    records = _load_history_records(history_file)
    record = _build_history_record(provider_key, tool, target_type, target_name, test_type, test_params, metrics, result_folder)
    records.append(record)

    _write_history_records(history_file, records)

    message = "Metrics added to history for analysis."
    return True, message

def load_history(target_type, target_name, test_type, limit=5):
    group_key = _build_group_key(target_type, target_name, test_type)
    history_file = _get_history_file(group_key)

    records = _load_history_records(history_file)

    if limit and len(records) > limit:
        return records[-limit:]

    return records