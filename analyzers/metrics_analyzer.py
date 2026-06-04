import os
from datetime import datetime

from config.settings import ANALYST_ROLE
from prompts.analysis_templates import build_analysis_prompt
from utils.llm_clients import call_openai, call_anthropic, call_gemini

class MetricsAnalyzer:
    def __init__(self, provider="openai", model=None):
        self.provider = provider

        if provider == "openai":
            self.model = model or "gpt-5.4"

        elif provider == "anthropic":
            self.model = model or "claude-sonnet-4-6"

        elif provider == "gemini":
            self.model = model or "gemini-3.1-pro-preview"

    def _call_model(self, prompt):
        if self.provider == "openai":
            return self._generate_openai(prompt)

        elif self.provider == "anthropic":
            return self._generate_anthropic(prompt)

        elif self.provider == "gemini":
            return self._generate_gemini(prompt)

    def _generate_openai(self, prompt):
        return call_openai(self.model, ANALYST_ROLE, prompt)

    def _generate_anthropic(self, prompt):
        return call_anthropic(self.model, ANALYST_ROLE, prompt)

    def _generate_gemini(self, prompt):
        return call_gemini(self.model, ANALYST_ROLE, prompt)

    def _build_report_header(self, target_type, target_name, test_type, tool):
        analysis_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return (
            "# Аналіз результатів тестування\n\n"
            f"**Модель:** {self.provider} / {self.model}\n"
            f"**Дата аналізу:** {analysis_date}\n"
            f"**Тест:** {target_type} / {target_name} / {test_type}\n"
            f"**Інструмент:** {tool}\n\n"
            "---\n\n"
        )

    def analyze(self, target_type, target_name, target_description, test_type, test_params, tool, metrics, history):
        prompt = build_analysis_prompt(target_type=target_type, target_name=target_name, target_description=target_description, test_type=test_type, test_params=test_params, tool=tool, current_metrics=metrics, history=history)

        model_response = self._call_model(prompt)
        header = self._build_report_header(target_type, target_name, test_type, tool)

        return header + model_response.strip()

    def save_report(self, report, result_folder):
        filename = f"analysis_{self.provider}.md"
        filepath = os.path.join(result_folder, filename)

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(report)

        return filepath