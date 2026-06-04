import os
import re
from prompts.endpoint_templates import build_endpoint_prompt
from prompts.flow_templates import build_flow_prompt
from prompts.parameters_templates import build_test_parameters_prompt
from config.settings import ENDPOINTS, MODEL_ROLE
from prompts.tool_rules import TOOL_RULES
from utils.llm_clients import call_openai, call_anthropic, call_gemini

class ScriptGenerator:
    FILE_EXTENSIONS = {"k6": ".js", "locust": ".py", "jmeter": ".jmx", "gatling": ".java"}
    MAX_ATTEMPTS = 3

    def __init__(self, provider="openai", model=None):
        self.provider = provider

        if provider == "openai":
            self.model = model or "gpt-5.4"

        elif provider == "anthropic":
            self.model = model or "claude-sonnet-4-6"

        elif provider == "gemini":
            self.model = model or "gemini-3.1-pro-preview"

    def _clean_code(self, code):
        code = code.strip()

        if code.startswith("```"):
            first_newline = code.find("\n")
            if first_newline != -1:
                code = code[first_newline + 1:]
            else:
                code = code[3:]

        if code.endswith("```"):
            code = code[:-3]

        return code.strip()

    def _validate_script(self, code, tool, paths):
        rules = TOOL_RULES.get(tool, {})
        errors = []

        for item in rules.get("required", []):
            if item not in code:
                errors.append(f"Missing required element: {item}")

        for item in rules.get("forbidden", []):
            if item in code:
                errors.append(f"Forbidden element found: {item}")

        cleaned = code.replace("${userId}", "").replace("${goalId}", "").replace("#{userId}", "").replace("#{goalId}", "")
        for placeholder in ("{userId}", "{goalId}"):
            if placeholder in cleaned:
                errors.append(f"Unresolved placeholder found: {placeholder}")

        for path in paths:
            for segment in self._extract_path_segments(path):
                if segment not in code:
                    errors.append(f"Endpoint path segment '{segment}' from '{path}' not found")
                    break

        if len(code.strip()) < 100:
            errors.append(f"Generated script is too short ({len(code.strip())} chars), likely empty or refusal")

        return errors

    @staticmethod
    def _extract_path_segments(path):
        no_placeholders = re.sub(r"\{[^}]+\}", "", path)
        return [segment for segment in no_placeholders.split("/") if segment]

    def _build_repair_prompt(self, original_prompt, broken_code, errors):
        error_text = "\n".join(f"- {error}" for error in errors)

        return f"""The generated script is invalid.

Original task:
{original_prompt}

Generated script:
{broken_code}

Problems:
{error_text}

Fix only these problems and return corrected code. Do not add explanations.""".strip()

    def _call_model(self, prompt):
        if self.provider == "openai":
            return self._generate_openai(prompt)

        elif self.provider == "anthropic":
            return self._generate_anthropic(prompt)

        elif self.provider == "gemini":
            return self._generate_gemini(prompt)

    def _generate_openai(self, prompt):
        return call_openai(self.model, MODEL_ROLE, prompt)

    def _generate_anthropic(self, prompt):
        return call_anthropic(self.model, MODEL_ROLE, prompt)

    def _generate_gemini(self, prompt):
        return call_gemini(self.model, MODEL_ROLE, prompt)

    def _generate_with_validation(self, prompt, tool, paths):
        current_prompt = prompt
        code = ""

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            code = self._clean_code(self._call_model(current_prompt))
            errors = self._validate_script(code, tool, paths)

            if not errors:
                if attempt > 1:
                    print(f"Repair successful on attempt {attempt}")
                return code

            print(f"Validation errors (attempt {attempt}/{self.MAX_ATTEMPTS}): {errors}")

            if attempt < self.MAX_ATTEMPTS:
                current_prompt = self._build_repair_prompt(prompt, code, errors)

        print(f"Could not fix all errors after {self.MAX_ATTEMPTS} attempts")
        return code

    def generate_endpoint(self, tool, endpoint_info, users=10, duration="30s", ramp_up="5s", test_type="load", description=""):
        rules = TOOL_RULES.get(tool, {})
        prompt = build_endpoint_prompt(tool, endpoint_info, users, duration, ramp_up, test_type, description, rules)
        paths = [endpoint_info["path"]]
        return self._generate_with_validation(prompt, tool, paths)

    def generate_user_flow(self, tool, scenario_info, users=10, duration="30s", ramp_up="5s", test_type="load"):
        rules = TOOL_RULES.get(tool, {})
        prompt = build_flow_prompt(tool, scenario_info, users, duration, ramp_up, test_type, rules)

        paths = [ENDPOINTS[step["endpoint"]]["path"] for step in scenario_info["steps"]]
        return self._generate_with_validation(prompt, tool, paths)

    def generate_test_parameters(self, test_type, test_type_info, target_type="", target_name="", target_description=""):
        prompt = build_test_parameters_prompt(test_type, test_type_info, target_type, target_name, target_description)

        return self._call_model(prompt)

    def save_script(self, code, tool, test_name="load_test", provider=""):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        if provider:
            folder = os.path.join(project_root, "generated_scripts", provider, tool)
        else:
            folder = os.path.join(project_root, "generated_scripts", tool)

        os.makedirs(folder, exist_ok=True)

        extension = self.FILE_EXTENSIONS[tool]
        filename = f"{test_name}{extension}"
        filepath = os.path.join(folder, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        return filepath