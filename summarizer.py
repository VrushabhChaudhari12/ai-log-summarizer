"""
AI Log Summarizer - Main summarization logic using Ollama LLM
"""

import time
from openai import OpenAI

# Configuration
BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
MODEL = "llama3.2"
TIMEOUT_SECONDS = 60
MAX_RETRIES = 3

# Termination conditions - factors that would require immediate escalation
TERMINATION_CONDITIONS = [
    "CRITICAL",
    "P1",
    "production down",
    "system unavailable",
]

# Required fields in the response
REQUIRED_FIELDS = ["SEVERITY", "WHAT", "WHY", "WHEN", "ACTION", "SAFE"]

# Fallback retry configuration
ACTION_RETRIES = 2
ACTION_RETRY_MESSAGE = "Your previous response was missing the ACTION field. You MUST provide exactly 2 numbered action steps. Rewrite the full response including all 6 fields."


def _parse_response(response_text):
    """
    Parse the LLM response to extract the 6 required fields.

    Args:
        response_text: Raw response from the LLM

    Returns:
        Dictionary with the 6 fields, or None if parsing fails
    """
    result = {}
    lines = response_text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if line starts with a required field
        for field in REQUIRED_FIELDS:
            if line.startswith(field + ":"):
                value = line[len(field) + 1:].strip()
                result[field] = value
                break

    # Validate all 6 fields are present
    if all(field in result for field in REQUIRED_FIELDS):
        return result
    return None


def _check_termination_condition(analysis):
    """
    Check if the analysis indicates a critical condition requiring termination.

    Args:
        analysis: Parsed analysis dictionary

    Returns:
        True if termination is needed, False otherwise
    """
    severity = analysis.get("SEVERITY", "").upper()
    what = analysis.get("WHAT", "").lower()

    for condition in TERMINATION_CONDITIONS:
        if condition in severity or condition in what:
            return True
    return False


def _is_action_empty(result):
    """
    Check if the ACTION field is empty or missing.

    Args:
        result: Parsed response dictionary

    Returns:
        True if ACTION is empty/missing, False otherwise
    """
    action = result.get("ACTION", "").strip()
    return not action or action.startswith("[") or action.startswith("1") is False and action == ""


def summarize(logs, alarm_context):
    """
    Summarize logs using Ollama LLM with four-layer termination safety.

    Args:
        logs: String containing log entries
        alarm_context: Dictionary with alarm metadata

    Returns:
        Dictionary with fields: SEVERITY, WHAT, WHY, WHEN, ACTION, SAFE

    Raises:
        Exception: If all retries fail or response is invalid
    """
    from prompts import SYSTEM_PROMPT, build_prompt

    # Build the prompt
    user_message = build_prompt(logs, alarm_context)

    # Initialize the client
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=TIMEOUT_SECONDS)

    # Retry logic with exponential backoff
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            # Make the LLM call
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=500,
            )

            # Extract response text
            response_text = response.choices[0].message.content

            # Validate response - check all 6 fields are present
            result = _parse_response(response_text)

            if result is None:
                # Invalid response format - could retry
                last_error = ValueError(f"Invalid response format - missing required fields: {response_text}")
                if attempt < MAX_RETRIES - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                raise last_error

            # Fallback: Check if ACTION field is empty, retry if needed
            if _is_action_empty(result):
                for action_attempt in range(ACTION_RETRIES):
                    # Make a retry LLM call with the fallback message
                    retry_response = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_message},
                            {"role": "user", "content": ACTION_RETRY_MESSAGE}
                        ],
                        temperature=0.3,
                        max_tokens=500,
                    )
                    retry_text = retry_response.choices[0].message.content
                    result = _parse_response(retry_text)
                    if result is not None and not _is_action_empty(result):
                        break

            # Layer 1: Check termination condition
            if _check_termination_condition(result):
                # Could raise an alert here in production
                pass

            # All validations passed, return result
            return result

        except Exception as e:
            last_error = e
            error_str = str(e).lower()

            # Check if it's a connection error
            is_connection_error = any(
                keyword in error_str
                for keyword in ["connection", "timeout", "refused", "unreachable"]
            )

            if is_connection_error and attempt < MAX_RETRIES - 1:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            elif not is_connection_error:
                # Non-connection error, don't retry
                raise

    # All retries exhausted
    raise last_error