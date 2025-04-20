import logging
import sys
from orchestrator.orchestrator import Orchestrator
from orchestrator.agents.sql_injection_agent import SQLInjectionAgent
from orchestrator.agents.xss_agent import XSSAgent
from orchestrator.task import Task
import docker
import time
import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from security_report import SecurityReport

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_session_with_retries():
    """Create a requests session with retry logic."""
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def wait_for_dvwa(session, base_url, max_retries=10, delay=5):
    """Wait for DVWA to be ready with retry logic."""
    for attempt in range(max_retries):
        try:
            response = session.get(f"{base_url}/setup.php", verify=False, timeout=5)
            if response.status_code == 200:
                logger.info("DVWA is ready!")
                return True
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries}: DVWA not ready yet. Error: {str(e)}")
        
        time.sleep(delay)
    
    raise Exception("DVWA failed to become ready in time")

def setup_dvwa():
    """Set up and configure the DVWA container."""
    logger.info("Setting up DVWA container...")
    client = docker.from_env()
    session = create_session_with_retries()
    base_url = "http://localhost:8080"
    
    try:
        # Stop and remove any existing containers
        for container in client.containers.list(all=True):
            try:
                if container.image.tags and "dvwa" in container.image.tags[0].lower():
                    logger.info(f"Stopping existing DVWA container: {container.id}")
                    container.stop()
                    container.remove()
            except Exception as e:
                logger.warning(f"Error handling container {container.id}: {str(e)}")
                continue
        
        # Pull the DVWA image
        logger.info("Pulling DVWA image...")
        client.images.pull("vulnerables/web-dvwa")
        
        # Run the container
        logger.info("Starting DVWA container...")
        container = client.containers.run(
            "vulnerables/web-dvwa",
            detach=True,
            ports={'80/tcp': 8080}
        )
        
        # Wait for container to be ready
        logger.info("Waiting for DVWA to be ready...")
        wait_for_dvwa(session, base_url)
        
        # Set up database
        logger.info("Setting up database...")
        setup_response = session.post(
            f"{base_url}/setup.php",
            data={"create_db": "Create / Reset Database"},
            verify=False,
            timeout=10
        )
        
        if setup_response.status_code != 200:
            raise Exception("Failed to set up DVWA database")
            
        time.sleep(5)  # Wait for database setup
        
        # Login to DVWA
        logger.info("Logging in to DVWA...")
        login_data = {
            'username': 'admin',
            'password': 'password',
            'Login': 'Submit'
        }
        
        login_response = session.post(
            f"{base_url}/login.php",
            data=login_data,
            verify=False,
            allow_redirects=True,
            timeout=10
        )
        
        if "Login failed" in login_response.text:
            raise Exception("Failed to log in to DVWA")
            
        # Set security level to low
        logger.info("Setting security level to low...")
        security_response = session.post(
            f"{base_url}/security.php",
            data={
                'security': 'low',
                'seclev_submit': 'Submit'
            },
            verify=False,
            timeout=10
        )
        
        # Verify we can access the vulnerabilities
        test_response = session.get(f"{base_url}/vulnerabilities/sqli/", verify=False, timeout=10)
        if test_response.status_code != 200:
            raise Exception("Failed to access DVWA vulnerabilities")
            
        logger.info("DVWA setup completed successfully")
        return container, session
        
    except Exception as e:
        logger.error(f"Error setting up DVWA: {str(e)}")
        if 'container' in locals():
            try:
                container.stop()
                container.remove()
            except:
                pass
        raise

def main():
    """Main function to run the tests."""
    try:
        # Set up DVWA
        container, session = setup_dvwa()
        report_manager = SecurityReport()
        
        try:
            # Initialize orchestrator
            orchestrator = Orchestrator()
            
            # Register agents
            sql_agent = SQLInjectionAgent()
            xss_agent = XSSAgent()
            orchestrator.register_agent(sql_agent)
            orchestrator.register_agent(xss_agent)
            
            # Create SQL injection task
            sql_task = orchestrator.create_task(
                name="DVWA SQL Injection Assessment",
                description="Test for SQL injection vulnerabilities in DVWA",
                parameters={
                    "target": "http://localhost:8080/vulnerabilities/sqli/",
                    "test_types": {"sql_injection"},
                    "difficulty": "low",
                    "session": session
                }
            )
            
            # Create XSS task
            xss_task = orchestrator.create_task(
                name="DVWA XSS Assessment",
                description="Test for XSS vulnerabilities in DVWA",
                parameters={
                    "target": "http://localhost:8080/vulnerabilities/xss_r/",
                    "test_types": {"xss"},
                    "difficulty": "low",
                    "session": session
                }
            )
            
            # Assign and execute tasks
            logger.info("Starting security assessment...")
            
            # Execute SQL injection test
            logger.info("Running SQL injection tests...")
            orchestrator.assign_task(sql_task.id, sql_agent.id)
            sql_result = sql_agent.execute_task(sql_task)
            logger.info(f"SQL injection test completed: {sql_result['status']}")
            
            # Save SQL injection report
            sql_report = report_manager.format_report(
                sql_result.get('findings', []),
                "sql_injection"
            )
            sql_report_path = report_manager.save_report(sql_report, "sql_injection")
            logger.info(f"SQL injection report saved to: {sql_report_path}")
            
            # Execute XSS test
            logger.info("Running XSS tests...")
            orchestrator.assign_task(xss_task.id, xss_agent.id)
            xss_result = xss_agent.execute_task(xss_task)
            logger.info(f"XSS test completed: {xss_result['status']}")
            
            # Save XSS report
            xss_report = report_manager.format_report(
                xss_result.get('findings', []),
                "xss"
            )
            xss_report_path = report_manager.save_report(xss_report, "xss")
            logger.info(f"XSS report saved to: {xss_report_path}")
            
            # Generate combined report
            combined_findings = sql_result.get('findings', []) + xss_result.get('findings', [])
            combined_report = report_manager.format_report(
                combined_findings,
                "combined_security_assessment"
            )
            combined_report_path = report_manager.save_report(combined_report, "combined")
            logger.info(f"Combined security report saved to: {combined_report_path}")
            
            # Log summary of findings
            logger.info("\nSecurity Assessment Summary:")
            logger.info(f"Total findings: {len(combined_findings)}")
            logger.info("Risk levels:")
            for level, count in combined_report['summary']['risk_levels'].items():
                logger.info(f"  {level.upper()}: {count}")
                
        finally:
            # Clean up
            logger.info("Cleaning up...")
            container.stop()
            container.remove()
            logger.info("DVWA container stopped and removed")
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 