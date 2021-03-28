import uvicorn
from loguru import logger

from server.api import app
from server.core import load_database

def start(port=8000):
    logger.info("Loading data...")
    load_database()

    logger.info(f"Start server on port {port}!")
    uvicorn.run(app, host="0.0.0.0", port=port)

