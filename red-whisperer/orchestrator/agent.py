import os
from openai import OpenAI
from typing import Dict, Any, Set
import logging
from datetime import datetime
from .task import Task
from config import OPENAI_API_KEY, HEARTBEAT_INTERVAL

class Agent:
    """Base class for AI-powered security testing agents."""
    
    def __init__(self, id: str, name: str, capabilities: Set[str]):
        self.id = id
        self.name = name
        self.capabilities = capabilities
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client with environment variable
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=api_key)
        
        # Initialize A2A compliance
        self.a2a = A2ACompliance()
        
        # Register agent
        self._register_agent()
        
    def analyze_vulnerability(self, context: str) -> Dict[str, Any]:
        """Use AI to analyze a potential vulnerability."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a security testing agent specialized in {', '.join(self.capabilities)}. Analyze the following vulnerability context and provide detailed insights."},
                    {"role": "user", "content": context}
                ]
            )
            return {
                "analysis": response.choices[0].message.content,
                "timestamp": datetime.now().isoformat(),
                "confidence": response.choices[0].finish_reason == "stop"
            }
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
    def plan_next_steps(self, current_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to plan the next testing steps based on current findings."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a security testing agent specialized in {', '.join(self.capabilities)}. Based on the current findings, suggest the next testing steps."},
                    {"role": "user", "content": str(current_findings)}
                ]
            )
            return {
                "next_steps": response.choices[0].message.content,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error in planning next steps: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a security testing task with AI guidance."""
        self.logger.info(f"Starting task execution: {task.id}")
        task.start()
        
        # Initialize results
        results = {
            "status": "in_progress",
            "findings": [],
            "ai_insights": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Get AI guidance for task execution
            guidance = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a security testing agent specialized in {', '.join(self.capabilities)}. Provide guidance for executing this security test."},
                    {"role": "user", "content": f"Task: {task.name}\nDescription: {task.description}\nParameters: {str(task.parameters)}"}
                ]
            )
            
            results["ai_insights"].append({
                "type": "guidance",
                "content": guidance.choices[0].message.content,
                "timestamp": datetime.now().isoformat()
            })
            
            # Execute the actual test (to be implemented by subclasses)
            test_results = self._execute_specific_test(task)
            results.update(test_results)
            
            # Analyze results with AI
            analysis = self.analyze_vulnerability(str(test_results))
            results["ai_insights"].append({
                "type": "analysis",
                "content": analysis,
                "timestamp": datetime.now().isoformat()
            })
            
            # Plan next steps
            next_steps = self.plan_next_steps(results)
            results["ai_insights"].append({
                "type": "next_steps",
                "content": next_steps,
                "timestamp": datetime.now().isoformat()
            })
            
            results["status"] = "completed"
            task.complete()
            
        except Exception as e:
            self.logger.error(f"Error executing task: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
            task.fail()
            
        return results
        
    def _execute_specific_test(self, task: Task) -> Dict[str, Any]:
        """Execute specific security test. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _execute_specific_test") 