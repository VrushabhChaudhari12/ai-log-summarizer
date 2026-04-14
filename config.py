import os

# LLM settings
BASE_URL = os.getenv("BASE_URL", "http://localhost:11434/v1")
API_KEY = os.getenv("API_KEY", "ollama")
MODEL = os.getenv("MODEL", "llama3.2")
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "60"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Output schema
REQUIRED_FIELDS = ["SEVERITY", "WHAT", "WHY", "WHEN", "ACTION", "SAFE"]
ACTION_RETRIES = int(os.getenv("ACTION_RETRIES", "2"))

# Escalation keywords
TERMINATION_CONDITIONS = ["CRITICAL", "P1", "production down", "system unavailable"]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
