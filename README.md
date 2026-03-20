# AI Log Summarizer

AI-powered CloudWatch log summarizer for AWS SRE teams.

## Overview

Single LLM call per incident to reduce triage time from 45 minutes to 2 minutes.

## Features

- **Structured Output**: P1/P2/P3 severity classification with root cause analysis
- **Slack Integration**: Formatted messages ready for incident channels
- **Fast Triage**: One LLM call per incident with response validation

## Stack

- Python
- Ollama (localhost:11434)
- llama3.2 model

## Setup

1. Ensure Ollama is running with llama3.2 model:
   ```bash
   ollama run llama3.2
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run

```bash
py main.py
```

This will process three sample incident scenarios:
- cpu_spike
- rds_connection
- disk_full