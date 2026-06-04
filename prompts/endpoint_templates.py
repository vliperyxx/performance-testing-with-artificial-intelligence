import json
from config.settings import API_CONTEXT, BASE_URL, TEST_USER_IDS, TEST_GOAL_IDS, TEST_USER_EMAILS
from prompts.tool_rules import TOOL_RULES, TOOL_EXAMPLES

def build_endpoint_prompt(tool, endpoint_info, users, duration, ramp_up, test_type="load", description="", rules=None):
    rules = rules or TOOL_RULES.get(tool, {"required": [], "forbidden": [], "notes": ""})
    method = endpoint_info["method"]
    path = endpoint_info["path"]
    full_url = BASE_URL + path

    body = endpoint_info.get("body")
    response = endpoint_info.get("response")

    body_str = json.dumps(body) if body else ""
    needs_user_ids = "{userId}" in path or "{userId}" in body_str
    needs_goal_ids = "{goalId}" in path

    test_ids_lines = []
    placeholders = []
    if needs_user_ids:
        test_ids_lines.append(f"Available test user IDs:\n{json.dumps(TEST_USER_IDS, indent=2)}")
        placeholders.append("{userId}")
    if needs_goal_ids:
        test_ids_lines.append(f"Available test goal IDs:\n{json.dumps(TEST_GOAL_IDS, indent=2)}")
        placeholders.append("{goalId}")

    test_ids_section = ""
    if test_ids_lines:
        placeholders_text = " and ".join(placeholders)
        test_ids_section = "\n" + "\n\n".join(test_ids_lines) + f"\n\nFor each virtual user or iteration, randomly select an ID from the appropriate list above to substitute every {placeholders_text} placeholder in the URL or body. Do not hardcode a single ID, do not leave placeholders unresolved."

    unique_fields = endpoint_info.get("unique_fields", [])

    needs_test_credentials = (body and "email" in body and "password" in body and "email" not in unique_fields)

    test_credentials_section = ""
    if needs_test_credentials:
        test_credentials_section = f"""
Available test login emails:
    {json.dumps(TEST_USER_EMAILS, indent=2)}

For each virtual user or iteration, randomly select an email from the list above to use in the request body. The password stays the same for all test users, use the password shown in the request body example. Do not hardcode a single email for all requests."""
    endpoint_description = endpoint_info.get("description", "")
    expected_status = endpoint_info.get("expected_status", 200)

    body_section = ""
    if body:
        body_section = f"""
Request body in JSON format:
{json.dumps(body, indent=2)}"""

    response_section = ""
    if response:
        response_section = f"""
Expected response example:
{json.dumps(response, indent=2)}"""

    unique_fields_section = ""
    if unique_fields:
        fields_list = "\n".join(f"- {field}" for field in unique_fields)
        unique_fields_section = f"""
Important: Each virtual user must generate unique values for these body fields to avoid conflicts and unrealistic duplicate data:
{fields_list}
Append a random uuid suffix or current timestamp to make each value unique per virtual user. Other body fields can stay as in the example."""

    required_text = "\n".join(f"- {requirement}" for requirement in rules.get("required", []))
    forbidden_text = "\n".join(f"- {restriction}" for restriction in rules.get("forbidden", []))

    prompt = f"""
Context: {API_CONTEXT}
You are testing this endpoint: {endpoint_description}

Endpoint details:
- Method: {method}
- URL: {full_url}
- Expected response status code: {expected_status}
{body_section}
{test_ids_section}
{test_credentials_section}
{unique_fields_section}
{response_section}

Task: Write a {test_type} performance test script for {tool}.
Test parameters:
- Virtual users: {users}
- Duration: {duration}
- Ramp-up: {ramp_up}
- Purpose: {description}

Strict rules for {tool} you must follow:
Required elements:
{required_text}

Never use these since they will cause errors:
{forbidden_text}

Additional notes: {rules.get("notes", "")}

Output format: Return only code, nothing else. Do not add extra endpoints or extra classes"""

    example = TOOL_EXAMPLES.get(tool, "")
    if example:
        prompt += f"""

Here is an example of a correct {tool} script for a different endpoint.
Use it only as a syntax and structure reference:
{example}
Adapt it to the endpoint described above. Change the URL, method, payload, status code, and test parameters accordingly."""

    return prompt.strip()