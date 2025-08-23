"""
Entry point for the Strategic Consultant Agent.
Initializes and starts the agent's server.
"""

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv
import os # Import os module

# Add the parent directory (backend) to the Python path to allow importing common
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Use relative imports within the agent package
from .task_manager import TaskManager
from .agent import root_agent
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

async def main():
    """Initialize and start the Strategic Consultant Agent server."""
    global task_manager_instance
    
    logger.info("Starting Strategic Consultant Agent A2A Server initialization...")
    
    # Initialize TaskManager
    task_manager_instance = TaskManager(agent=root_agent)
    logger.info("TaskManager initialized with agent instance.")

    # Configuration for the A2A server
    # For Railway deployment: use 0.0.0.0 and PORT environment variable
    host = os.getenv("CONSULTANT_A2A_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("CONSULTANT_A2A_PORT", "8004")))
    
    # Create the FastAPI app using the helper
    app = create_agent_server(
        name=root_agent.name,
        description=root_agent.description,
        task_manager=task_manager_instance
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
