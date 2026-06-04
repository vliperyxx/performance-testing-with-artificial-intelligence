import json

from config.settings import API_CONTEXT, TEST_TYPES

def _format_history_record(record):
    return {"timestamp": record.get("timestamp"), "tool": record.get("tool"), "load_parameters": record.get("load_parameters"), "metrics": record.get("metrics")}

def _format_history_section(history):
    if not history:
        return "No previous runs available for this target and test type."

    compact_records = [_format_history_record(record) for record in history]
    return json.dumps(compact_records, indent=2, ensure_ascii=False)

def build_analysis_prompt(target_type, target_name, target_description, test_type, test_params, tool, current_metrics, history):
    test_type_info = TEST_TYPES.get(test_type, {})
    test_type_description = test_type_info.get("description", "")

    history_section = _format_history_section(history)
    current_metrics_json = json.dumps(current_metrics, indent=2, ensure_ascii=False)

    prompt = f"""Context: {API_CONTEXT}
This is a local development environment, not production.

Test target:
- Type: {target_type}
- Name: {target_name}
- Description: {target_description}

Test configuration:
- Test type: {test_type} ({test_type_description})
- Virtual users: {test_params.get("virtual_users")}
- Duration: {test_params.get("duration")}
- Ramp-up: {test_params.get("ramp_up")}
- Tool: {tool}

Current test metrics:
{current_metrics_json}

Previous runs for the same target and test type (oldest first, most recent last):
{history_section}

Task: Analyze the current test metrics together with previous runs and provide a concise report with three sections.

Output format:
Return a markdown response with exactly these three Ukrainian section headings:

## Оцінка продуктивності
Briefly assess whether the current metrics meet expectations for this test type and load level, and mention noticeable trends across runs.

## Виявлені проблеми та аномалії
List concrete issues visible in the metrics: high error rate, slow percentiles, response time growth across runs, unstable throughput. Only report what the data actually shows. If there are no issues, say so explicitly.

## Рекомендації
Suggest specific, actionable improvements based on the issues above. If no issues were found, suggest what to watch in future runs.

Rules:
- Entire response must be in Ukrainian
- Total response length: 200-400 words
- Do not invent metrics that are not in the input
- Do not give generic advice unrelated to the metrics
- Do not suggest production-grade infrastructure changes (load balancers, replicas, CDN, autoscaling)
- Do not use emoji or decorative symbols"""

    return prompt.strip()