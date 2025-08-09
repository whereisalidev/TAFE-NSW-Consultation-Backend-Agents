"""
Entry point for the Strategic Consultant Agent.
Initializes and starts the agent's server.
"""

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv

# Use relative imports within the agent package
from .task_manager import TaskManager, SimpleCapacityTaskManager, SimpleRiskTaskManager, SimpleEngagementTaskManager
from .agent import root_agent, capacity_agent, risk_agent, engagement_agent
from common.a2a_server import create_agent_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path, override=True)

# Global variable for the TaskManager instance
task_manager_instance: TaskManager = None
capacity_task_manager_instance: SimpleCapacityTaskManager = None
risk_task_manager_instance: SimpleRiskTaskManager = None
engagement_task_manager_instance: SimpleEngagementTaskManager = None

from common.a2a_server import AgentRequest, AgentResponse
from fastapi import Body

async def capacity_agent_endpoint(request: AgentRequest = Body(...)):
    """Custom endpoint for the capacity assessment agent."""
    global capacity_task_manager_instance
    
    try:        
        result = await capacity_task_manager_instance.process_task(
            request.message, 
            request.context, 
            request.session_id
        )
        
        return AgentResponse(
            message=result.get("message", "Hello! I'm Morgan, your capacity analyst. Let's assess your department's capacity."),
            status=result.get("status", "success"),
            data=result.get("data", {}),
            session_id=result.get("session_id", request.session_id)
        )
    except Exception as e:
        return AgentResponse(
            message=f"Error processing capacity assessment request: {str(e)}",
            status="error",
            data={"error_type": type(e).__name__},
            session_id=request.session_id
        )

async def risk_agent_endpoint(request: AgentRequest = Body(...)):
    """Custom endpoint for the risk assessment agent."""
    global risk_task_manager_instance
    
    try:        
        result = await risk_task_manager_instance.process_task(
            request.message, 
            request.context, 
            request.session_id
        )
        
        return AgentResponse(
            message=result.get("message", "Hello! I'm Alex, your risk assessment specialist. Let's identify and assess potential risks."),
            status=result.get("status", "success"),
            data=result.get("data", {}),
            session_id=result.get("session_id", request.session_id)
        )
    except Exception as e:
        return AgentResponse(
            message=f"Error processing risk assessment request: {str(e)}",
            status="error",
            data={"error_type": type(e).__name__},
            session_id=request.session_id
        )

async def engagement_agent_endpoint(request: AgentRequest = Body(...)):
    """Custom endpoint for the stakeholder engagement agent."""
    global engagement_task_manager_instance
    
    try:        
        result = await engagement_task_manager_instance.process_task(
            request.message, 
            request.context, 
            request.session_id
        )
        
        return AgentResponse(
            message=result.get("message", "G'day! I'm Jordan, your engagement specialist. Let's develop a comprehensive stakeholder engagement strategy."),
            status=result.get("status", "success"),
            data=result.get("data", {}),
            session_id=result.get("session_id", request.session_id)
        )
    except Exception as e:
        return AgentResponse(
            message=f"Error processing engagement planning request: {str(e)}",
            status="error",
            data={"error_type": type(e).__name__},
            session_id=request.session_id
        )

async def main():
    """Initialize and start the Strategic Consultant Agent server."""
    global task_manager_instance, capacity_task_manager_instance, risk_task_manager_instance, engagement_task_manager_instance
    
    logger.info("Starting Strategic Consultant Agent A2A Server initialization...")
    
    # Initialize all TaskManagers
    task_manager_instance = TaskManager(agent=root_agent)
    capacity_task_manager_instance = SimpleCapacityTaskManager(agent=capacity_agent)
    risk_task_manager_instance = SimpleRiskTaskManager(agent=risk_agent)
    engagement_task_manager_instance = SimpleEngagementTaskManager(agent=engagement_agent)
    logger.info("All TaskManagers initialized with agent instances.")

    # Configuration for the A2A server
    # For Railway deployment: use 0.0.0.0 and PORT environment variable
    host = os.getenv("CONSULTANT_A2A_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("CONSULTANT_A2A_PORT", "8004")))
    
    # Define additional endpoints
    additional_endpoints = {
        "capacity-agent": capacity_agent_endpoint,
        "risk-agent": risk_agent_endpoint,
        "engagement-agent": engagement_agent_endpoint
    }
    
    # Create the FastAPI app using the helper
    app = create_agent_server(
        name=root_agent.name,
        description=root_agent.description,
        task_manager=task_manager_instance,
        endpoints=additional_endpoints
    )
    
    logger.info(f"Strategic Consultant Agent A2A server starting on {host}:{port}")
    
    # Configure uvicorn
    import uvicorn
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    
    # Run the server
    await server.serve()
    
    # This part will be reached after the server is stopped (e.g., Ctrl+C)
    logger.info("Strategic Consultant Agent A2A server stopped.")

if __name__ == "__main__":
    try:
        # Run the async main function
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Strategic Consultant Agent server stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error during server startup: {str(e)}", exc_info=True)
        sys.exit(1)