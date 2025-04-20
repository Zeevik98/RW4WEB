import json
from datetime import datetime
from typing import Dict, Any
import os

class SecurityReport:
    """Handles security test report generation and storage."""
    
    def __init__(self, base_dir: str = "reports"):
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            
    def save_report(self, report_data: Dict[str, Any], test_type: str) -> str:
        """Save a security test report to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_type}_report_{timestamp}.json"
        filepath = os.path.join(self.base_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=4, default=str)
            
        return filepath
        
    @staticmethod
    def format_report(findings: list, test_type: str) -> Dict[str, Any]:
        """Format the test results into a structured report."""
        return {
            "test_type": test_type,
            "timestamp": datetime.now().isoformat(),
            "findings": findings,
            "summary": {
                "total_findings": len(findings),
                "risk_levels": {
                    "critical": len([f for f in findings if f.get("severity") == "critical"]),
                    "high": len([f for f in findings if f.get("severity") == "high"]),
                    "medium": len([f for f in findings if f.get("severity") == "medium"]),
                    "low": len([f for f in findings if f.get("severity") == "low"])
                }
            }
        } 