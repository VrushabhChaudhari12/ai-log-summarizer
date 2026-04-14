"""
AI Log Summarizer - Main summarization logic using Ollama LLM.
Refactored: uses config module, structured logging, typed return values.
"""
import logging
import time
from typing import Dict, Optional

from openai import OpenAI
import config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("summarizer")

ACTION_RETRY_MESSAGE = (
    "Your previous response was missing the ACTION field. "
    "You MUST provide exactly 2 numbered action steps. "
    "Rewrite the full response including all 6 fields."
)

_client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
    timeout=config.TIMEOUT_SECONDS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _parse_response(response_text: str) -> Optional[Dict[str, str]]:
    """Extract the 6 required fields from the LLM response."""
    result: Dict[str, str] = {}
    lines = response_text.strip().splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        for field in config.REQUIRED_FIELDS:
            if line.startswith(field + ":"):
                result[field] = line[len(field) + 1:].strip()
                break
    return result if all(f in result for f in config.REQUIRED_FIELDS) else None


def _check_termination(analysis: Dict[str, str]) -> bool:
    """Return True if the summary indicates a critical condition."""
    text = " ".join(analysis.values()).lower()
    return any(kw.lower() in text for kw in config.TERMINATION_CONDITIONS)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def summarize_logs(log_content: str, log_group: str = "unknown") -> Dict:
    """
    Summarize CloudWatch logs using the LLM.

    Args:
        log_content: Raw log text to analyze.
        log_group:   Descriptive name of the log group (for logging).

    Returns:
        Dict with analysis fields plus 'escalate' bool and 'processing_time_seconds'.
    """
    logger.info("Starting log summarization for group: %s", log_group)
    start = time.time()

    from prompts import build_messages
    messages = build_messages(log_content)

    action_retries = 0

    for attempt in range(1, config.MAX_RETRIES + 1):
        elapsed = time.time() - start
        if elapsed > config.TIMEOUT_SECONDS:
            logger.error("Timeout after %.1fs on attempt %d", elapsed, attempt)
            return {"error": f"Timeout after {elapsed:.1f}s", "escalate": False}

        try:
            response = _client.chat.completions.create(
                model=config.MODEL,
                messages=messages,
                temperature=0.1,
                max_tokens=400,
            )
            response_text = response.choices[0].message.content
            logger.debug("LLM response (attempt %d): %s", attempt, response_text[:120])
        except Exception as exc:
            logger.error("LLM call failed on attempt %d: %s", attempt, exc)
            time.sleep(2 ** attempt)
            continue

        analysis = _parse_response(response_text)
        if not analysis:
            logger.warning("Parse failed on attempt %d. Missing required fields.", attempt)
            # Retry with correction hint if ACTION field is specifically missing
            if action_retries < config.ACTION_RETRIES:
                messages.append({"role": "assistant", "content": response_text})
                messages.append({"role": "user", "content": ACTION_RETRY_MESSAGE})
                action_retries += 1
            time.sleep(1)
            continue

        escalate = _check_termination(analysis)
        analysis["escalate"] = escalate
        analysis["processing_time_seconds"] = round(time.time() - start, 2)
        if escalate:
            logger.warning("CRITICAL condition detected - escalation required!")
        logger.info("Summarization complete in %.2fs", analysis["processing_time_seconds"])
        return analysis

    logger.error("All %d attempts exhausted without a valid response.", config.MAX_RETRIES)
    return {"error": f"Failed after {config.MAX_RETRIES} retries", "escalate": False}
