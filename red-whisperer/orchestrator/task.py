from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime

@dataclass
class Task:
    """Represents a security testing task."""
    
    id: str
    name: str
    description: str
    parameters: Dict
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    assigned_agent: Optional[str] = None
    
    def assign_agent(self, agent_id: str) -> None:
        """Assign the task to an agent."""
        self.assigned_agent = agent_id
        self.status = "assigned"
        
    def start(self) -> None:
        """Mark the task as started."""
        if not self.assigned_agent:
            raise ValueError("Cannot start task without assigned agent")
        self.status = "in_progress"
        
    def complete(self) -> None:
        """Mark the task as completed."""
        self.status = "completed"
        self.completed_at = datetime.now()
        
    def fail(self, error: Optional[str] = None) -> None:
        """Mark the task as failed."""
        self.status = "failed"
        if error:
            self.parameters["error"] = error
        self.completed_at = datetime.now() 