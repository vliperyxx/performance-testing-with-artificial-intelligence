import os
import sys
import json
import re
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import TEST_TYPES, MODELS, PERFORMANCE_TOOLS, ENDPOINTS, SCENARIOS
from ui_labels import TEST_TYPE_LABELS, MODEL_LABELS, TOOL_LABELS, ENDPOINT_LABELS, SCENARIO_LABELS, LOAD_SETUP_LABELS, TARGET_TYPE_LABELS
from generators.script_generator import ScriptGenerator
from analyzers.metrics_parsers import PARSERS
from analyzers.metrics_history import save_to_history, load_history
from runners.test_runner import RUNNERS, save_result_folder, delete_result_folder
from analyzers.metrics_analyzer import MetricsAnalyzer

app = Flask(__name__)
CORS(app)

def _build_test_types():
    return [
        {"key": key, "label": TEST_TYPE_LABELS.get(key, key), "virtual_users": info["virtual_users"], "duration": info["duration"], "ramp_up": info["ramp_up"]}
        for key, info in TEST_TYPES.items()
    ]

def _build_models():
    return [
        {"key": key, "label": MODEL_LABELS.get(key, info["name"])}
        for key, info in MODELS.items()
    ]

def _build_tools():
    return [
        {"key": tool, "label": TOOL_LABELS.get(tool, tool)}
        for tool in PERFORMANCE_TOOLS
    ]

def _build_endpoints():
    return [
        {"key": key, "label": ENDPOINT_LABELS.get(key, key)}
        for key in ENDPOINTS.keys()
    ]

def _build_scenarios():
    return [
        {"key": key, "label": SCENARIO_LABELS.get(key, key)}
        for key in SCENARIOS.keys()
    ]

def _build_load_setup_options():
    return [
        {"key": key, "label": label}
        for key, label in LOAD_SETUP_LABELS.items()
    ]

def _build_target_types():
    return [
        {"key": key, "label": label}
        for key, label in TARGET_TYPE_LABELS.items()
    ]

def _build_test_name(target_type, target_name, test_type):
    return f"{target_type}_{target_name}_{test_type}"

def _parse_params_response(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError("Could not find JSON object in model response")
    return json.loads(match.group(0))

def _get_target_description(target_type, target_name):
    if target_type == "endpoint":
        return ENDPOINTS[target_name].get("description", "")
    if target_type == "flow":
        return SCENARIOS[target_name].get("description", "")
    return ""

def _strip_markdown(text):
    if not text:
        return ""

    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'^---+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify({"test_types": _build_test_types(), "models": _build_models(), "tools": _build_tools(), "endpoints": _build_endpoints(), "scenarios": _build_scenarios(), "load_setup_options": _build_load_setup_options(), "target_types": _build_target_types()})

@app.route("/api/generate-params", methods=["POST"])
def generate_params_endpoint():
    data = request.get_json()
    test_type = data["test_type"]
    target_type = data["target_type"]
    target_name = data["target_name"]
    model_key = data["model"]

    model_name = MODELS[model_key]["name"]
    generator = ScriptGenerator(provider=model_key, model=model_name)

    response_text = generator.generate_test_parameters(test_type=test_type, test_type_info=TEST_TYPES[test_type], target_type=target_type, target_name=target_name, target_description=_get_target_description(target_type, target_name))

    return jsonify({"params": _parse_params_response(response_text)})

@app.route("/api/generate", methods=["POST"])
def generate_script():
    data = request.get_json()

    target_type = data["target_type"]
    target_name = data["target_name"]
    test_type = data["test_type"]
    model_key = data["model"]
    tools = data["tools"]

    custom_params = data.get("custom_params")
    test_params = custom_params if custom_params else TEST_TYPES[test_type]
    model_name = MODELS[model_key]["name"]

    generator = ScriptGenerator(provider=model_key, model=model_name)
    results = []

    for tool in tools:
        if target_type == "endpoint":
            code = generator.generate_endpoint(tool=tool, endpoint_info=ENDPOINTS[target_name], users=test_params["virtual_users"], duration=test_params["duration"], ramp_up=test_params["ramp_up"], test_type=test_type)
        else:
            code = generator.generate_user_flow(tool=tool, scenario_info=SCENARIOS[target_name], users=test_params["virtual_users"], duration=test_params["duration"], ramp_up=test_params["ramp_up"], test_type=test_type)

        results.append({"tool": tool, "model": model_key, "code": code})

    return jsonify({"scripts": results})

@app.route("/api/save", methods=["POST"])
def save_script_endpoint():
    data = request.get_json()

    code = data["code"]
    tool = data["tool"]
    provider = data["provider"]
    target_type = data["target_type"]
    target_name = data["target_name"]
    test_type = data["test_type"]
    test_params = data["test_params"]

    test_name = _build_test_name(target_type, target_name, test_type)
    model_name = MODELS[provider]["name"]

    generator = ScriptGenerator(provider=provider, model=model_name)
    script_path = generator.save_script(code, tool, test_name=test_name, provider=provider)

    config = {"target_type": target_type, "target_name": target_name, "test_type": test_type, "test_params": test_params, "tool": tool, "provider": provider, "model": model_name}
    extension = ScriptGenerator.FILE_EXTENSIONS[tool]
    config_path = script_path.replace(extension, "_config.json")
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=2, ensure_ascii=False)

    return jsonify({"script_path": script_path, "config_path": config_path})

@app.route("/api/run-test", methods=["POST"])
def run_test_endpoint():
    data = request.get_json()

    script_path = data["script_path"]
    tool = data["tool"]
    target_type = data["target_type"]
    target_name = data["target_name"]
    test_type = data["test_type"]
    test_params = data["test_params"]
    provider = data["provider"]

    runner = RUNNERS.get(tool)
    if not runner:
        return jsonify({"error": f"No runner for tool: {tool}"}), 400

    temp_folder = runner(script_path=script_path, test_params=test_params, provider_key=provider, target_type=target_type, target_name=target_name, test_type=test_type)

    parser = PARSERS.get(tool)
    metrics = parser(temp_folder) if parser else None

    return jsonify({"temp_folder": temp_folder, "metrics": metrics})

@app.route("/api/save-results", methods=["POST"])
def save_results_endpoint():
    data = request.get_json()
    temp_folder = data["temp_folder"]
    tool = data["tool"]
    provider = data["provider"]
    target_type = data["target_type"]
    target_name = data["target_name"]
    test_type = data["test_type"]
    test_params = data["test_params"]

    result_folder = save_result_folder(temp_folder, provider, tool)
    save_to_history(provider, tool, target_type, target_name, test_type, test_params, result_folder)

    return jsonify({"result_folder": result_folder})

@app.route("/api/delete-results", methods=["POST"])
def delete_results_endpoint():
    data = request.get_json()
    delete_result_folder(data["temp_folder"])

    return jsonify({"deleted": True})

@app.route("/api/analyze", methods=["POST"])
def analyze_endpoint():
    data = request.get_json()
    result_folder = data["result_folder"]
    tool = data["tool"]
    target_type = data["target_type"]
    target_name = data["target_name"]
    test_type = data["test_type"]
    test_params = data["test_params"]
    analyst_provider = data["analyst_provider"]

    parser = PARSERS.get(tool)
    metrics = parser(result_folder)
    if not metrics:
        return jsonify({"error": "Could not parse metrics"}), 400

    history = load_history(target_type, target_name, test_type)
    analyst_model = MODELS[analyst_provider]["name"]
    analyzer = MetricsAnalyzer(provider=analyst_provider, model=analyst_model)

    report = analyzer.analyze(target_type=target_type, target_name=target_name, target_description=_get_target_description(target_type, target_name), test_type=test_type, test_params=test_params, tool=tool, metrics=metrics, history=history)

    return jsonify({"report": report, "report_clean": _strip_markdown(report)})

@app.route("/api/save-analysis", methods=["POST"])
def save_analysis_endpoint():
    data = request.get_json()
    analyzer = MetricsAnalyzer(provider=data["analyst_provider"])
    saved_path = analyzer.save_report(data["report"], data["result_folder"])

    return jsonify({"saved_path": saved_path})

@app.route("/api/saved-scripts", methods=["GET"])
def saved_scripts_endpoint():
    scripts_root = project_root/"generated_scripts"
    if not scripts_root.exists():
        return jsonify({"scripts": []})

    scripts = []
    for provider_folder in scripts_root.iterdir():
        if not provider_folder.is_dir():
            continue
        for tool_folder in provider_folder.iterdir():
            if not tool_folder.is_dir():
                continue
            for file_path in tool_folder.iterdir():
                if not file_path.is_file() or file_path.name.endswith("_config.json"):
                    continue

                config_path = tool_folder/f"{file_path.stem}_config.json"
                if not config_path.exists():
                    continue

                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)

                scripts.append({"provider": provider_folder.name, "tool": tool_folder.name, "script_name": file_path.stem, "script_path": str(file_path), "config": config, "mtime": file_path.stat().st_mtime})

    scripts.sort(key=lambda s: s["mtime"], reverse=True)
    return jsonify({"scripts": scripts})

@app.route("/api/saved-results", methods=["GET"])
def saved_results_endpoint():
    results_root = project_root/"results"
    if not results_root.exists():
        return jsonify({"results": []})

    folder_pattern = re.compile(
        r"^(endpoint|flow)_(.+)_(load|stress|spike|endurance|scalability)_(\d{8}_\d{6})$"
    )

    results = []
    for provider_folder in results_root.iterdir():
        if not provider_folder.is_dir():
            continue
        for tool_folder in provider_folder.iterdir():
            if not tool_folder.is_dir():
                continue
            for result_folder in tool_folder.iterdir():
                if not result_folder.is_dir():
                    continue

                match = folder_pattern.match(result_folder.name)
                if not match:
                    continue

                target_type, target_name, test_type, timestamp = match.groups()
                test_params = None
                config_file = result_folder/"test_config.json"
                if config_file.exists():
                    with open(config_file, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                        test_params = cfg.get("test_params")

                analyzed_by = [
                    provider_key for provider_key in MODELS.keys()
                    if (result_folder/f"analysis_{provider_key}.md").exists()
                ]

                results.append({"provider": provider_folder.name, "tool": tool_folder.name, "result_folder": str(result_folder), "target_type": target_type, "target_name": target_name, "test_type": test_type, "test_params": test_params, "timestamp": timestamp, "analyzed_by": analyzed_by})

    results.sort(key=lambda r: r["timestamp"], reverse=True)
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)