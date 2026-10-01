from fastapi import FastAPI
from app.routers import router
from config.logging_config import setup_logging
import logging

# Configurar logging estructurado en JSON (Twelve-Factor: Factor 11)
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="ms-pdf-extract", description="Microservicio de extracción de texto de PDF")

app.include_router(router)

logger.info("ms-pdf-extract iniciado correctamente.")