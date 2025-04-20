import os
from dotenv import load_dotenv
from typing import List
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class BaseConfig:
    """Base configuration class for the application."""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    A2A_AUTH_TOKEN = os.getenv("A2A_AUTH_TOKEN")
    
    # A2A Configuration
    A2A_VERSION = "1.0.0"
    A2A_DISCOVERY_ENABLED = True
    A2A_HEALTH_CHECK_ENABLED = True
    A2A_AUTH_ENABLED = True
    AGENT_REGISTRY_URL = "http://localhost:8000/registry"
    
    # Required environment variables
    REQUIRED_ENV_VARS = [
        "OPENAI_API_KEY",
        "A2A_AUTH_TOKEN"
    ]
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Agent Configuration
    AGENT_HEALTH_CHECK_INTERVAL = int(os.getenv("AGENT_HEALTH_CHECK_INTERVAL", "60"))
    AGENT_DISCOVERY_INTERVAL = int(os.getenv("AGENT_DISCOVERY_INTERVAL", "300"))
    
    # Security Configuration
    MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Report Configuration
    REPORT_FORMAT = os.getenv("REPORT_FORMAT", "json")
    REPORT_DIRECTORY = os.getenv("REPORT_DIRECTORY", "reports/")
    
    # Authentication
    A2A_AUTH_EXPIRY = int(os.getenv("A2A_AUTH_EXPIRY", "3600"))  # 1 hour
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration."""
        missing_vars = [var for var in cls.REQUIRED_ENV_VARS if not getattr(cls, var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}") 