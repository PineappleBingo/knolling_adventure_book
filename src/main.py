"""
Knolling Adventures - Main Entry Point
Initializes Agent Omega (Orchestrator) and Agent Foxtrot (UI).
"""

import logging
from src.modules.orchestrator import AgentOmega
from src.modules.bot_interface import AgentFoxtrot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/system.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Main function to start the application.
    """
    logger.info("Starting Knolling Adventures Factory...")
    
    # Initialize Agents
    omega = AgentOmega()
    foxtrot = AgentFoxtrot(omega)
    
    # Start the Bot
    foxtrot.start()

if __name__ == "__main__":
    main()
