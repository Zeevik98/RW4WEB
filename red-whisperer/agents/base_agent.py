import sys
import os
import uuid
import time
import requests
import structlog
from datetime import datetime
from typing import Dict, Any, Optional

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import (
    ORCHESTRATOR_HOST,
    ORCHESTRATOR_PORT,
    HEARTBEAT_INTERVAL,
    MAX_RETRY_ATTEMPTS,
    RETRY_DELAY
)

class BaseAgent:
    def __init__(self, agent_type: str):
        self.agent_id = str(uuid.uuid4())
        self.agent_type = agent_type
        self.orchestrator_url = f"http://{ORCHESTRATOR_HOST}:{ORCHESTRATOR_PORT}"
        self.status = "initializing"
        self.capabilities = []
        
        # Configure logging
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()
            ]
        )
        self.logger = structlog.get_logger()

    async def register(self):
        """Register the agent with the orchestrator."""
        try:
            response = requests.post(
                f"{self.orchestrator_url}/agents/register",
                json={
                    "agent_id": self.agent_id,
                    "agent_type": self.agent_type,
                    "status": self.status,
                    "last_heartbeat": datetime.utcnow().isoformat(),
                    "capabilities": self.capabilities
                }
            )
            response.raise_for_status()
            self.logger.info("agent_registered", agent_id=self.agent_id)
        except Exception as e:
            self.logger.error("registration_failed", error=str(e))
            raise

    async def send_heartbeat(self):
        """Send periodic heartbeat to orchestrator."""
        while True:
            try:
                response = requests.post(
                    f"{self.orchestrator_url}/agents/register",
                    json={
                        "agent_id": self.agent_id,
                        "agent_type": self.agent_type,
                        "status": self.status,
                        "last_heartbeat": datetime.utcnow().isoformat(),
                        "capabilities": self.capabilities
                    }
                )
                response.raise_for_status()
                self.logger.debug("heartbeat_sent", agent_id=self.agent_id)
            except Exception as e:
                self.logger.error("heartbeat_failed", error=str(e))
            
            time.sleep(HEARTBEAT_INTERVAL)

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return results."""
        raise NotImplementedError("Subclasses must implement execute_task")

    def log_activity(self, event: str, **kwargs):
        """Log agent activity with structured logging."""
        self.logger.info(event, agent_id=self.agent_id, **kwargs)

    def update_status(self, new_status: str):
        """Update agent status and log the change."""
        old_status = self.status
        self.status = new_status
        self.logger.info(
            "status_changed",
            agent_id=self.agent_id,
            old_status=old_status,
            new_status=new_status
        ) 