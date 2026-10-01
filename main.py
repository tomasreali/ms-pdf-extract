from fastapi import FastAPI
from app.routers import router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ms-pdf-extract", description="Microservicio de extracción de texto de PDF")

app.include_router(router)

logger.info("ms-pdf-extract iniciado correctamente.")