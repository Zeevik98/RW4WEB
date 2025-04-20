import asyncio
import sys
import os
from typing import Dict, Any
from ..base_agent import BaseAgent
from openai import OpenAI

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import OPENAI_API_KEY, HEARTBEAT_INTERVAL

class SQLInjectionAgent(BaseAgent):
    def __init__(self):
        super().__init__("sql_injection")
        self.capabilities = [
            "sql_injection_detection",
            "sql_injection_exploitation",
            "database_enumeration"
        ]
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.update_status("ready")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQL injection testing task."""
        try:
            self.update_status("executing")
            self.log_activity("task_started", task_id=task["task_id"])

            # Use GPT-4 to generate SQL injection payloads
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a security expert specializing in SQL injection testing. Generate safe and effective SQL injection payloads for testing purposes."},
                    {"role": "user", "content": f"Generate SQL injection payloads for testing the following target: {task['target']}"}
                ]
            )

            # Process the generated payloads
            payloads = response.choices[0].message.content.split("\n")
            
            results = {
                "task_id": task["task_id"],
                "status": "completed",
                "payloads_generated": len(payloads),
                "payloads": payloads,
                "vulnerabilities_found": []  # This would be populated with actual test results
            }

            self.log_activity(
                "task_completed",
                task_id=task["task_id"],
                payloads_generated=len(payloads)
            )
            self.update_status("ready")
            
            return results

        except Exception as e:
            self.log_activity(
                "task_failed",
                task_id=task["task_id"],
                error=str(e)
            )
            self.update_status("error")
            raise

async def main():
    agent = SQLInjectionAgent()
    await agent.register()
    
    # Start heartbeat in background
    asyncio.create_task(agent.send_heartbeat())
    
    # Keep the agent running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main()) 