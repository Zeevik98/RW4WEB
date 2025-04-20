from typing import Dict, List, Optional, Any, Set
from .task import Task
from .agent import Agent
import uuid
import requests
from datetime import datetime
import json
import logging

class Orchestrator:
    """Orchestrates security testing tasks and agents."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.agents: Dict[str, Agent] = {}
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
    def register_agent(self, agent: Agent) -> None:
        """Register a new agent."""
        self.agents[agent.id] = agent
        self.logger.info(f"Registered agent {agent.id}: {agent.name}")
        
    def create_task(self, name: str, description: str, parameters: Dict) -> Task:
        """Create a new task."""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            name=name,
            description=description,
            parameters=parameters
        )
        self.tasks[task_id] = task
        self.logger.info(f"Created task {task_id}: {name}")
        return task
        
    def assign_task(self, task_id: str, agent_id: str) -> None:
        """Assign a task to an agent."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
            
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
            
        task = self.tasks[task_id]
        agent = self.agents[agent_id]
        
        # Assign the task
        task.assign_agent(agent_id)
        self.logger.info(f"Assigned task {task_id} to agent {agent_id}")
        
    async def execute_task(self, task_id: str) -> Dict:
        """Execute a task using its assigned agent."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
            
        task = self.tasks[task_id]
        if not task.assigned_agent:
            raise ValueError(f"Task {task_id} has no assigned agent")
            
        agent = self.agents[task.assigned_agent]
        return await agent.execute_task(task)
        
    def get_task_status(self, task_id: str) -> str:
        """Get the status of a task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        return self.tasks[task_id].status
        
    def get_agent_status(self, agent_id: str) -> str:
        """Get the status of an agent."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        return self.agents[agent_id].status
        
    async def generate_report(self, task: Task) -> Dict:
        """Generate a report for a completed task."""
        if task.id not in self.tasks:
            raise ValueError(f"Task {task.id} not found")
            
        if not task.assigned_agent:
            raise ValueError(f"Task {task.id} has no assigned agent")
            
        agent = self.agents[task.assigned_agent]
        return await agent.analyze_results(task.parameters.get("findings", []))
        
    def get_available_agents(self) -> List[Agent]:
        """Get all available (idle) agents."""
        return [agent for agent in self.agents.values() if agent.status == "idle"]
        
    def aggregate_results(self, task: Task) -> Dict[str, Any]:
        """Aggregate results from multiple agents for a task."""
        results = {
            "summary": {},
            "vulnerabilities": [],
            "recommendations": []
        }
        
        # Collect results from all subtasks
        for subtask_id in task.parameters.get("subtasks", []):
            subtask = self.tasks.get(subtask_id)
            if subtask and subtask.status == "completed":
                results["vulnerabilities"].extend(subtask.parameters.get("findings", []))
                
        # Generate recommendations based on findings
        results["recommendations"] = self._generate_recommendations(results["vulnerabilities"])
        
        # Create summary
        results["summary"] = {
            "total_vulnerabilities": len(results["vulnerabilities"]),
            "critical_count": len([v for v in results["vulnerabilities"] if v.get("severity") == "critical"]),
            "high_count": len([v for v in results["vulnerabilities"] if v.get("severity") == "high"]),
            "medium_count": len([v for v in results["vulnerabilities"] if v.get("severity") == "medium"]),
            "low_count": len([v for v in results["vulnerabilities"] if v.get("severity") == "low"])
        }
        
        return results
        
    def generate_report(self, task: Task) -> Dict[str, Any]:
        """Generate a detailed security assessment report."""
        results = self.aggregate_results(task)
        
        report = {
            "executive_summary": {
                "overview": f"Security assessment of {task.parameters.get('target')}",
                "total_findings": results["summary"]["total_vulnerabilities"],
                "risk_level": self._calculate_risk_level(results["summary"]),
                "assessment_date": datetime.now().isoformat()
            },
            "technical_details": {
                "target": task.parameters.get("target"),
                "test_types": task.parameters.get("test_types", []),
                "findings": results["vulnerabilities"]
            },
            "remediation_steps": results["recommendations"]
        }
        
        return report
        
    def _generate_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate remediation recommendations based on vulnerabilities."""
        recommendations = []
        
        for vuln in vulnerabilities:
            recommendation = {
                "vulnerability": vuln.get("name"),
                "severity": vuln.get("severity"),
                "description": vuln.get("description"),
                "remediation": vuln.get("remediation", "No specific remediation steps provided."),
                "priority": self._get_priority(vuln.get("severity"))
            }
            recommendations.append(recommendation)
            
        return sorted(recommendations, key=lambda x: x["priority"])
        
    def _calculate_risk_level(self, summary: Dict[str, Any]) -> str:
        """Calculate overall risk level based on vulnerability counts."""
        if summary["critical_count"] > 0 or summary["high_count"] > 2:
            return "Critical"
        elif summary["high_count"] > 0 or summary["medium_count"] > 2:
            return "High"
        elif summary["medium_count"] > 0 or summary["low_count"] > 2:
            return "Medium"
        else:
            return "Low"
            
    def _get_priority(self, severity: str) -> int:
        """Get priority level based on severity."""
        priorities = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4
        }
        return priorities.get(severity.lower(), 5) 