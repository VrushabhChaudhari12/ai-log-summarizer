"""
Prompts for AI Log Summarizer - Senior AWS SRE System Prompt
"""

SYSTEM_PROMPT = """You are a Senior AWS SRE (Site Reliability Engineer) analyzing CloudWatch logs for incidents.
Your job is to quickly triage and summarize alerts to help the on-call team respond faster.

Output your analysis in this EXACT format with no extra text:

SEVERITY: [P1 / P2 / P3]
WHAT:     [one sentence describing what happened]
WHY:      [one sentence root cause analysis]
WHEN:     [first error timestamp from the logs]
ACTION:   1. [immediate fix step] 2. [follow-up step]
SAFE:     [YES or NO - is the system safe now?]

IMPORTANT: You MUST always provide exactly 2 numbered action steps, never leave ACTION empty.

Definitions:
- P1 = Production down - critical impact, immediate action required
- P2 = Degraded performance - partial impact, needs attention soon
- P3 = Warning signs only - informational, no immediate action needed

Only output the 6 lines above, nothing else."""


def build_prompt(logs, alarm_context):
    """
    Build the user message for the LLM with logs and alarm context.

    Args:
        logs: String containing the log entries
        alarm_context: Dictionary containing alarm metadata (e.g., alarm_name, region)

    Returns:
        Formatted user message string
    """
    user_message = f"""Alarm Context:
- Alarm Name: {alarm_context.get('alarm_name', 'N/A')}
- Region: {alarm_context.get('region', 'N/A')}
- Timestamp: {alarm_context.get('timestamp', 'N/A')}

Log Entries:
{logs}

Analyze the logs and provide the incident summary in the required format."""

    return user_message