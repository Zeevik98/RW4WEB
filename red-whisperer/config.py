"""
Configuration settings for the Red-Whisperer system.
This file serves as a single source of truth for all configuration values.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# A2A Compliance Settings
A2A_VERSION = "1.0.0"
A2A_DISCOVERY_ENABLED = True
A2A_HEALTH_CHECK_ENABLED = True
A2A_AUTH_ENABLED = True

# Agent Registry
AGENT_REGISTRY_URL = os.getenv("AGENT_REGISTRY_URL", "http://localhost:8000/registry")

# Authentication
A2A_AUTH_TOKEN = os.getenv("A2A_AUTH_TOKEN")
A2A_AUTH_EXPIRY = int(os.getenv("A2A_AUTH_EXPIRY", "3600"))  # 1 hour

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Report Configuration
REPORT_FORMAT = os.getenv("REPORT_FORMAT", "json")
REPORT_DIRECTORY = os.getenv("REPORT_DIRECTORY", "reports/")

# Agent Configuration
AGENT_HEALTH_CHECK_INTERVAL = int(os.getenv("AGENT_HEALTH_CHECK_INTERVAL", "60"))
AGENT_DISCOVERY_INTERVAL = int(os.getenv("AGENT_DISCOVERY_INTERVAL", "300"))

# Security Configuration
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# Orchestrator Configuration
ORCHESTRATOR_HOST = "0.0.0.0"
ORCHESTRATOR_PORT = 8000

# Logging Configuration
LOG_DIR = "/var/log/red-whisperer"

# Security Configuration
ENABLE_IMMUTABLE_LOGS = True
MAX_LOG_RETENTION_DAYS = 90

# Agent Configuration
HEARTBEAT_INTERVAL = 30  # seconds
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds

# Network Configuration
DEFAULT_NETWORK = "red-whisperer-net"
DEFAULT_NETWORK_DRIVER = "bridge" 