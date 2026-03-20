"""
AI Log Summarizer - Main entry point

Runs all three incident scenarios one by one and prints formatted summaries.
"""

from mock_logs import get_log_string
from summarizer import summarize
from slack_notifier import post_to_slack


# Define the scenarios to run
SCENARIOS = [
    "cpu_spike",
    "rds_connection",
    "disk_full",
]

# Alarm context templates for each scenario
ALARM_CONTEXTS = {
    "cpu_spike": {
        "alarm_name": "HighCPUUtilization",
        "region": "us-east-1",
    },
    "rds_connection": {
        "alarm_name": "RDSConnectionFailures",
        "region": "us-west-2",
    },
    "disk_full": {
        "alarm_name": "DiskSpaceCritical",
        "region": "eu-west-1",
    },
}


def run_scenario(scenario_name):
    """
    Run a single scenario: get logs, summarize, and post to Slack.

    Args:
        scenario_name: The scenario key (e.g., "cpu_spike")
    """
    # Print scenario name
    print(f"\n{'='*60}")
    print(f"  SCENARIO: {scenario_name.upper()}")
    print(f"{'='*60}\n")

    # Get logs
    logs = get_log_string(scenario_name)

    # Get alarm context
    alarm = ALARM_CONTEXTS[scenario_name]

    # Summarize
    summary = summarize(logs, alarm)

    # Post to Slack
    post_to_slack(summary, alarm)

    # Add separator between scenarios
    print("\n" + "=" * 60 + "\n")


def main():
    """Run all scenarios sequentially."""
    print("\n" + "=" * 60)
    print("  AI LOG SUMMARIZER - Incident Triage")
    print("=" * 60 + "\n")

    for scenario in SCENARIOS:
        run_scenario(scenario)

    print("\nAll scenarios completed.")


if __name__ == "__main__":
    main()