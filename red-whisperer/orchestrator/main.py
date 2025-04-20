from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging
import structlog
from datetime import datetime
import sys
import os
import uuid

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, ORCHESTRATOR_HOST, ORCHESTRATOR_PORT, LOG_LEVEL, LOG_DIR

class Task(BaseModel):
    task_id: str
    task_type: str
    target: str
    parameters: Dict
    priority: int = 1
    created_at: datetime = datetime.utcnow()
    status: str = "created"
    assigned_agent: Optional[str] = None
    results: Optional[Dict] = None
    subtasks: Optional[List[Dict]] = None
    aggregated_results: Optional[Dict] = None

class AgentStatus(BaseModel):
    agent_id: str
    agent_type: str
    status: str
    last_heartbeat: datetime
    capabilities: List[str]

class Orchestrator:
    def __init__(self):
        self.active_tasks: Dict[str, Task] = {}
        self.agent_statuses: Dict[str, AgentStatus] = {}
        
    def register_agent(self, agent):
        """Register a new agent with the orchestrator."""
        agent_status = AgentStatus(
            agent_id=agent.id,  # Use the agent's ID instead of generating a new one
            agent_type=agent.name,
            status="active",
            last_heartbeat=datetime.utcnow(),
            capabilities=agent.capabilities
        )
        self.agent_statuses[agent_status.agent_id] = agent_status
        return agent_status
        
    def create_task(self, task_data: Dict):
        """Create a new task and assign it to an appropriate agent."""
        task = Task(
            task_id=str(uuid.uuid4()),
            task_type=task_data["type"],
            target=task_data["target"],
            parameters=task_data["parameters"]
        )
        
        # Find an appropriate agent for the task
        for agent_status in self.agent_statuses.values():
            if task.task_type in agent_status.capabilities:
                task.assigned_agent = agent_status.agent_id
                break
        
        self.active_tasks[task.task_id] = task
        return task
        
    def get_agent_tasks(self, agent_id: str) -> List[Task]:
        """Get tasks assigned to a specific agent."""
        return [task for task in self.active_tasks.values() if task.assigned_agent == agent_id]
        
    def list_agents(self) -> List[AgentStatus]:
        """List all registered agents."""
        return list(self.agent_statuses.values())

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

app = FastAPI(
    title="Red-Whisperer Orchestrator",
    description="Multi-Agent Red Teaming Orchestration System",
    version="1.0.0"
)

# In-memory storage (replace with proper database in production)
active_tasks: Dict[str, Task] = {}
agent_statuses: Dict[str, AgentStatus] = {}

@app.post("/tasks/", response_model=Task)
async def create_task(task: Task):
    """Create a new task and assign it to appropriate agents."""
    try:
        # Validate task type
        if task.task_type not in ["sql_injection", "xss", "phishing", "comprehensive"]:
            raise HTTPException(status_code=400, detail="Invalid task type")

        # Generate task ID if not provided
        if not task.task_id:
            task.task_id = str(uuid.uuid4())

        # Handle comprehensive tasks
        if task.task_type == "comprehensive":
            task.subtasks = []
            for test_type in task.parameters.get("tests", []):
                subtask_id = str(uuid.uuid4())
                subtask = Task(
                    task_id=subtask_id,
                    task_type=test_type,
                    target=task.target,
                    parameters=task.parameters,
                    status="created"
                )
                task.subtasks.append(subtask.dict())
                active_tasks[subtask_id] = subtask

        # Store task
        active_tasks[task.task_id] = task
        
        # Log task creation
        logger.info(
            "task_created",
            task_id=task.task_id,
            task_type=task.task_type,
            target=task.target
        )
        
        return task
    except Exception as e:
        logger.error("task_creation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Retrieve a specific task by ID."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return active_tasks[task_id]

@app.post("/tasks/{task_id}/update", response_model=Task)
async def update_task(task_id: str, update_data: Dict):
    """Update task status and results."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    task.status = update_data.get("status", task.status)
    task.results = update_data.get("results", task.results)
    
    # Update parent task if this is a subtask
    for parent_task in active_tasks.values():
        if parent_task.subtasks:
            for subtask in parent_task.subtasks:
                if subtask["task_id"] == task_id:
                    subtask.update(update_data)
                    # Check if all subtasks are completed
                    if all(st["status"] == "completed" for st in parent_task.subtasks):
                        parent_task.status = "completed"
                        parent_task.aggregated_results = {
                            "subtask_results": [st.get("results", {}) for st in parent_task.subtasks]
                        }
    
    return task

@app.post("/agents/register", response_model=AgentStatus)
async def register_agent(agent_status: AgentStatus):
    """Register a new agent or update existing agent status."""
    try:
        agent_statuses[agent_status.agent_id] = agent_status
        logger.info(
            "agent_registered",
            agent_id=agent_status.agent_id,
            agent_type=agent_status.agent_type
        )
        return agent_status
    except Exception as e:
        logger.error("agent_registration_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/", response_model=List[AgentStatus])
async def list_agents():
    """List all registered agents."""
    return list(agent_statuses.values())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=ORCHESTRATOR_HOST, port=ORCHESTRATOR_PORT) 