from config.settings import API_CONTEXT

def build_test_parameters_prompt(test_type, test_type_info, target_type="", target_name="", target_description=""):
    prompt = f"""Context: {API_CONTEXT}

Test target:
- Target type: {target_type}
- Target name: {target_name}
- Target description: {target_description}

Selected test type:
- Type: {test_type}
- Description: {test_type_info["description"]}

Task: Suggest reasonable load testing parameters for this test type.

You must provide these parameters:
- virtual_users (number of virtual users)
- duration (total test duration)
- ramp_up (time needed to gradually increase the load)
- reason (short explanation why these parameters are suitable) 

Important rules that you have to follow:
- Parameters must be realistic for a local project environment
- Do not suggest extremely high values
- The values must match the selected test type based on its description

Output format: Return only valid JSON and don't add explanations outside it.
The "reason" field must be written in Ukrainian. All other fields stay numeric or in the same format as the example.

Expected JSON structure:
{{
  "virtual_users": 50,
  "duration": "5m",
  "ramp_up": "30s",
  "reason": "Ці параметри відображають типове очікуване навантаження для локальної API системи."
}}"""

    return prompt.strip()