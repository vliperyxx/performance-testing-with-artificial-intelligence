import csv
import os
import json

PERCENTILE_COLUMNS = {"median_ms": "50%", "p90_ms": "90%", "p95_ms": "95%", "p99_ms": "99%"}

def _to_int(value):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0

def _to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def _extract_response_time(row):
    response_time = {"avg_ms": _to_int(row.get("Average Response Time")), "min_ms": _to_int(row.get("Min Response Time")), "max_ms": _to_int(row.get("Max Response Time"))}

    for output_key, column_name in PERCENTILE_COLUMNS.items():
        response_time[output_key] = _to_int(row.get(column_name))

    return response_time

def _build_metrics_from_row(row):
    total_requests = _to_int(row.get("Request Count"))
    failed_requests = _to_int(row.get("Failure Count"))

    if total_requests > 0:
        error_rate = round((failed_requests/total_requests) * 100, 2)
    else:
        error_rate = 0.0

    return {"total_requests": total_requests, "failed_requests": failed_requests, "error_rate_percent": error_rate, "throughput_rps": round(_to_float(row.get("Requests/s")), 2), "response_time": _extract_response_time(row)}

def _read_locust_failures(failures_file):
    if not os.path.exists(failures_file):
        return []

    errors = []

    with open(failures_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            errors.append({"method": row.get("Method", "").strip(), "name": row.get("Name", "").strip(), "error": row.get("Error", "").strip(), "occurrences": _to_int(row.get("Occurrences"))})

    return errors

def parse_locust_results(result_folder):
    stats_file = os.path.join(result_folder, "locust_result_stats.csv")

    if not os.path.exists(stats_file):
        return None

    aggregated_row = None

    with open(stats_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row.get("Name", "").strip() == "Aggregated":
                aggregated_row = row
                break

    if aggregated_row is None:
        return None

    result = {"aggregated": _build_metrics_from_row(aggregated_row)}

    if result["aggregated"]["failed_requests"] > 0:
        failures_file = os.path.join(result_folder, "locust_result_failures.csv")
        errors = _read_locust_failures(failures_file)

        if errors:
            result["errors"] = errors

    return result

def _extract_k6_response_time(duration_metric):
    return {"avg_ms": _to_int(duration_metric.get("avg")), "min_ms": _to_int(duration_metric.get("min")), "max_ms": _to_int(duration_metric.get("max")), "median_ms": _to_int(duration_metric.get("med")), "p90_ms": _to_int(duration_metric.get("p(90)")), "p95_ms": _to_int(duration_metric.get("p(95)")), "p99_ms": _to_int(duration_metric.get("p(99)"))}

def parse_k6_results(result_folder):
    summary_file = os.path.join(result_folder, "k6_summary.json")

    if not os.path.exists(summary_file):
        return None

    with open(summary_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    metrics = data.get("metrics", {})
    http_reqs = metrics.get("http_reqs")
    http_req_duration = metrics.get("http_req_duration")

    if not http_reqs or not http_req_duration:
        return None

    total_requests = _to_int(http_reqs.get("count"))
    failure_rate = _to_float(metrics.get("http_req_failed", {}).get("value"))
    failed_requests = round(failure_rate * total_requests)

    if total_requests > 0:
        error_rate_percent = round(failure_rate * 100, 2)
    else:
        error_rate_percent = 0.0

    return {"aggregated": {"total_requests": total_requests, "failed_requests": failed_requests, "error_rate_percent": error_rate_percent, "throughput_rps": round(_to_float(http_reqs.get("rate")), 2), "response_time": _extract_k6_response_time(http_req_duration)}}

GATLING_METRIC_LABELS = {"request count": "total_requests", "min response time (ms)": "min_ms", "max response time (ms)": "max_ms", "mean response time (ms)": "avg_ms", "response time 50th percentile (ms)": "median_ms", "response time 90th percentile (ms)": "p90_ms", "response time 95th percentile (ms)": "p95_ms", "response time 99th percentile (ms)": "p99_ms", "mean throughput (rps)": "throughput_rps"}

def _parse_gatling_value(value_text):
    cleaned = value_text.strip().replace(",", "")

    if cleaned == "-" or cleaned == "":
        return None

    return cleaned

def _read_gatling_global_info(output_file):
    if not os.path.exists(output_file):
        return None, None

    total_column = {}
    ko_column = {}

    with open(output_file, "r", encoding="utf-8") as file:
        for line in file:
            if not line.startswith("> "):
                continue

            parts = line.split("|")

            if len(parts) < 4:
                continue

            label = parts[0].replace(">", "").strip()

            if label not in GATLING_METRIC_LABELS:
                continue

            total_value = _parse_gatling_value(parts[1])
            ko_value = _parse_gatling_value(parts[3])

            output_key = GATLING_METRIC_LABELS[label]
            total_column[output_key] = total_value
            ko_column[output_key] = ko_value

    return total_column, ko_column

def parse_gatling_results(result_folder):
    output_file = os.path.join(result_folder, "run_output.txt")
    total_column, ko_column = _read_gatling_global_info(output_file)

    if not total_column or "total_requests" not in total_column:
        return None

    total_requests = _to_int(total_column.get("total_requests"))
    failed_requests = _to_int(ko_column.get("total_requests"))

    if total_requests > 0:
        error_rate_percent = round((failed_requests/total_requests) * 100, 2)
    else:
        error_rate_percent = 0.0

    response_time_keys = ["avg_ms", "min_ms", "max_ms", "median_ms", "p90_ms", "p95_ms", "p99_ms"]
    response_time = {key: _to_int(total_column.get(key)) for key in response_time_keys}

    return {"aggregated": {"total_requests": total_requests, "failed_requests": failed_requests, "error_rate_percent": error_rate_percent, "throughput_rps": round(_to_float(total_column.get("throughput_rps")), 2), "response_time": response_time}}

def parse_jmeter_results(result_folder):
    statistics_file = os.path.join(result_folder, "html_report", "statistics.json")

    if not os.path.exists(statistics_file):
        return None

    with open(statistics_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    total_section = data.get("Total")

    if not total_section:
        return None

    total_requests = _to_int(total_section.get("sampleCount"))
    failed_requests = _to_int(total_section.get("errorCount"))

    if total_requests > 0:
        error_rate_percent = round(_to_float(total_section.get("errorPct")), 2)
    else:
        error_rate_percent = 0.0

    response_time = {"avg_ms": _to_int(total_section.get("meanResTime")), "min_ms": _to_int(total_section.get("minResTime")), "max_ms": _to_int(total_section.get("maxResTime")), "median_ms": _to_int(total_section.get("medianResTime")), "p90_ms": 0, "p95_ms": _to_int(total_section.get("pct2ResTime")), "p99_ms": _to_int(total_section.get("pct3ResTime"))}

    return {"aggregated": {"total_requests": total_requests, "failed_requests": failed_requests, "error_rate_percent": error_rate_percent, "throughput_rps": round(_to_float(total_section.get("throughput")), 2), "response_time": response_time}}

PARSERS = {"locust": parse_locust_results, "k6": parse_k6_results, "jmeter": parse_jmeter_results, "gatling": parse_gatling_results}