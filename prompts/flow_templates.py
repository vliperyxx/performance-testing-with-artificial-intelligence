import json
from config.settings import API_CONTEXT, BASE_URL, ENDPOINTS, TEST_USER_EMAILS
from prompts.tool_rules import TOOL_RULES, TOOL_EXAMPLES


def _format_step(step, step_number):
    endpoint_key = step["endpoint"]
    endpoint = ENDPOINTS[endpoint_key]

    method = endpoint["method"]
    path = endpoint["path"]
    full_url = BASE_URL + path

    lines = [f"Step {step_number}: {step['action'].replace('_', ' ').title()}"]
    expected = endpoint.get("expected_status", 200)
    lines.append(f"- {method} {full_url} (expected status: {expected})")

    if endpoint.get("body"):
        lines.append(f"- Request body: {json.dumps(endpoint['body'])}")

    unique_fields = endpoint.get("unique_fields", [])
    if unique_fields:
        fields_text = ", ".join(unique_fields)
        lines.append(f"- Body fields that must be unique per virtual user: {fields_text}")

    if step.get("extract"):
        lines.append(f"- Extract from response: {', '.join(step['extract'])}")

    if step.get("use_from_previous"):
        lines.append(f"- Use from previous steps: {', '.join(step['use_from_previous'])}")

    if step.get("note"):
        lines.append(f"- Note: {step['note']}")

    return "\n".join(lines)


def build_flow_prompt(tool, scenario_info, users, duration, ramp_up, test_type="load", rules=None):
    rules = rules or TOOL_RULES.get(tool, {"required": [], "forbidden": [], "notes": ""})

    steps = scenario_info["steps"]
    scenario_description = scenario_info["description"]

    needs_test_credentials = False
    for i, step in enumerate(steps):
        if step["endpoint"] == "login":
            previous_was_register = i > 0 and steps[i - 1]["endpoint"] == "register"
            if not previous_was_register:
                needs_test_credentials = True
                break

    test_credentials_section = ""
    if needs_test_credentials:
        test_credentials_section = f"""

Available test login emails:
{json.dumps(TEST_USER_EMAILS, indent=2)}

For the login step in this scenario, randomly select an email from the list above to use in the request body. The password stays the same for all test users, use the password shown in the login body example. Do not hardcode a single email for all virtual users."""

    steps_text = "\n\n".join(_format_step(step, i + 1) for i, step in enumerate(steps))

    required_text = "\n".join(f"- {requirement}" for requirement in rules.get("required", []))
    forbidden_text = "\n".join(f"- {restriction}" for restriction in rules.get("forbidden", []))

    prompt = f"""Context: {API_CONTEXT}

You are writing a user flow scenario test. A virtual user must execute all steps in order, where each step can use data from previous steps.

Scenario: {scenario_description}

Steps to execute sequentially:

{steps_text}
{test_credentials_section}

Task: Write a {test_type} performance test script for {tool}.
Test parameters:
- Virtual users: {users}
- Duration: {duration}
- Ramp-up: {ramp_up}

Key requirements for user flow:
- Replace placeholders like {{userId}} or {{goalId}} in URLs with values extracted from previous steps. Do not leave placeholders or hardcode sample UUIDs.
- For each step, generate unique values for the fields marked as "must be unique per virtual user" using a random uuid suffix or current timestamp
- Reuse shared values across steps, don't regenerate
- Validate response status after each step
- If any step fails, skip the rest for that user

Strict rules for {tool} you must follow:
Required elements:
{required_text}

Never use these since they will cause errors:
{forbidden_text}

Additional notes: {rules.get("notes", "")}

Output format: Return only code, nothing else. Do not add extra scenarios or extra classes."""

    example = TOOL_EXAMPLES.get(tool, "")
    if example:
        prompt += f"""

Here is an example of a correct single endpoint {tool} script.
Use it only as a syntax and structure reference:

{example}
Adapt it to the user flow described above. The example shows a single endpoint, your output must chain all scenario steps."""

    return prompt.strip()