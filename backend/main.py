import os
from api import app
from api.utils.logging_utils import setup_logging
from core.config import settings
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app='api:app', host=settings.FASTAPI_HOST, port=settings.FASTAPI_PORT, reload=settings.RELOAD)