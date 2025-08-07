import logging
from core.config import settings

def setup_logging():
    logging.basicConfig(
        level=settings.FASTAPI_LOG_LEVEL.upper(),
        format="%(asctime)s - %(levelname)s - %(message)s"
    )