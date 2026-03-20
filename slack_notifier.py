"""
Slack Notifier - Formats and prints incident summaries in Slack-style output
"""

from datetime import datetime


def post_to_slack(summary, alarm):
    """
    Print a formatted Slack-style message to console.

    Args:
        summary: Dictionary with fields: SEVERITY, WHAT, WHY, WHEN, ACTION, SAFE
        alarm: Dictionary with alarm metadata (alarm_name, region, timestamp)
    """
    # Header
    header = "=" * 60
    print(header)
    print(f" :rotating_light: *INCIDENT ALERT* :rotating_light:")
    print(header)

    # Divider
    divider = "-" * 60
    print(divider)

    # Alarm info
    print(f"*Alarm Name:* {alarm.get('alarm_name', 'N/A')}")
    print(f"*Region:* {alarm.get('region', 'N/A')}")
    print(divider)

    # Summary fields
    print(f"*SEVERITY:* {summary.get('SEVERITY', 'N/A')}")
    print(f"*WHAT:* {summary.get('WHAT', 'N/A')}")
    print(f"*WHY:* {summary.get('WHY', 'N/A')}")
    print(f"*WHEN:* {summary.get('WHEN', 'N/A')}")
    print(f"*ACTION:* {summary.get('ACTION', 'N/A')}")
    print(f"*SAFE:* {summary.get('SAFE', 'N/A')}")

    # Footer with timestamp
    print(divider)
    footer = "=" * 60
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f" _Generated at {timestamp}_ ")
    print(footer)
    print()