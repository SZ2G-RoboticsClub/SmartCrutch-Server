from server import app
import uvicorn
from loguru import logger

PORT = 8080
logger.info(f"Start server on port {PORT}!")
uvicorn.run(app, host="0.0.0.0", port=PORT)