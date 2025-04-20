from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class TaskStatus(Enum):
    """Enum for task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Task:
    """Class representing a security testing task."""
    
    def __init__(self, id: str, name: str, description: str, parameters: Optional[Dict[str, Any]] = None):
        self.id = id
        self.name = name
        self.description = description
        self.parameters = parameters or {}
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.error = None
        
    def start(self):
        """Start the task execution."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
        
    def complete(self):
        """Mark the task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        
    def fail(self, error: str = None):
        """Mark the task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error
        } 