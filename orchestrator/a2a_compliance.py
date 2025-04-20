import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from config.base import BaseConfig

logger = logging.getLogger(__name__)

class A2ACompliance:
    """Handles A2A compliance requirements for agents."""
    
    def __init__(self):
        self.config = BaseConfig
        self.last_heartbeat = None
        self.registered = False
        
    def register_agent(self, agent_info: Dict[str, Any]) -> bool:
        """Register agent with the A2A registry."""
        if not self.config.A2A_DISCOVERY_ENABLED:
            logger.info("A2A discovery is disabled")
            return True
            
        try:
            headers = {
                "Authorization": f"Bearer {self.config.A2A_AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.config.AGENT_REGISTRY_URL}/register",
                json=agent_info,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.registered = True
                logger.info("Agent registered successfully")
                return True
            else:
                logger.error(f"Failed to register agent: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error registering agent: {str(e)}")
            return False
            
    def send_heartbeat(self, agent_id: str) -> bool:
        """Send health check heartbeat to registry."""
        if not self.config.A2A_HEALTH_CHECK_ENABLED:
            return True
            
        try:
            headers = {
                "Authorization": f"Bearer {self.config.A2A_AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.config.AGENT_REGISTRY_URL}/heartbeat",
                json={"agent_id": agent_id, "timestamp": datetime.now().isoformat()},
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                self.last_heartbeat = datetime.now()
                return True
            else:
                logger.error(f"Heartbeat failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending heartbeat: {str(e)}")
            return False
            
    def check_version_compatibility(self, other_version: str) -> bool:
        """Check if agent version is compatible with another version."""
        try:
            # Simple semantic versioning check
            our_major = int(self.config.A2A_VERSION.split('.')[0])
            their_major = int(other_version.split('.')[0])
            return our_major == their_major
        except Exception:
            return False
            
    def validate_auth_token(self, token: str) -> bool:
        """Validate authentication token."""
        if not self.config.A2A_AUTH_ENABLED:
            return True
            
        try:
            headers = {
                "Authorization": f"Bearer {self.config.A2A_AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.config.AGENT_REGISTRY_URL}/validate_token",
                json={"token": token},
                headers=headers,
                timeout=5
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return False
            
    def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities for discovery."""
        return {
            "version": self.config.A2A_VERSION,
            "capabilities": ["xss", "sql_injection", "csrf", "ssrf"],
            "supported_protocols": ["http", "https"],
            "max_concurrent_tasks": self.config.MAX_CONCURRENT_TASKS,
            "rate_limit": self.config.RATE_LIMIT_PER_MINUTE
        } 