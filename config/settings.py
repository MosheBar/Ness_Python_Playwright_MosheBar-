import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Global config variables
GRID_URL = os.getenv("GRID_URL")
USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ECommerceFramework")
