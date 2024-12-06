import logging

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,  # Default log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
