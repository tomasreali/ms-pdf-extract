from fastapi import APIRouter, UploadFile, File, HTTPException
import logging
import time
from datetime import datetime, timezone
from config.settings import settings
from service.extract_service import extraer_texto
from service.summary_client import solicitar_resumen
from app.models.extract_response import ExtractResponse
from app.models.extract_and_summarize_response import ExtractAndSummarizeResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Variables para health check mejorado (Tarea 8)
_start_time = time.time()
_version = "1.0.0"


@router.get("/health")
async def health_check():
    """Health check mejorado con uptime y versión (Twelve-Factor App, Factor 11)."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": _version,
        "uptime_seconds": round(time.time() - _start_time, 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/extract", response_model=ExtractResponse)
async def extract_text(file: UploadFile = File(...)):
    """Extrae texto de un archivo PDF."""
    start = time.time()
    logger.info(f"Request recibido: POST /extract - archivo: {file.filename}")

    # Validación de extensión
    if not file.filename.endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF válido.")

    # Lectura y validación de tamaño
    contenido = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(contenido) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo es demasiado grande. Máximo permitido: {settings.max_file_size_mb}MB."
        )

    # Delegamos al service
    resultado = extraer_texto(contenido)

    duration = round((time.time() - start) * 1000, 2)
    logger.info(f"Extracción exitosa: {resultado['page_count']} páginas - {duration}ms")
    return resultado


@router.post("/extract-and-summarize", response_model=ExtractAndSummarizeResponse)
async def extract_and_summarize(file: UploadFile = File(...)):
    """
    Extrae texto del PDF y solicita un resumen al microservicio de IA.
    Si el servicio de IA no responde, devuelve solo el texto (degradación elegante).

    Patrón aplicado: Chain (material del profesor)
    """
    start = time.time()
    logger.info(f"Request recibido: POST /extract-and-summarize - archivo: {file.filename}")

    # Validación de extensión
    if not file.filename.endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF válido.")

    # Lectura y validación de tamaño
    contenido = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(contenido) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo es demasiado grande. Máximo permitido: {settings.max_file_size_mb}MB."
        )

    # 1. Extraer texto (reutilizar lógica existente)
    resultado_extraccion = extraer_texto(contenido)

    logger.info(f"Texto extraído: {resultado_extraccion['page_count']} páginas. Solicitando resumen a ms-ia-summary...")

    # 2. Solicitar resumen al microservicio de IA (con retry + circuit breaker)
    resultado_resumen = await solicitar_resumen(resultado_extraccion["content"])

    duration = round((time.time() - start) * 1000, 2)

    # 3. Construir respuesta con degradación elegante
    if "error" in resultado_resumen:
        logger.warning(f"Resumen no disponible: {resultado_resumen['error']} - {duration}ms")
        return ExtractAndSummarizeResponse(
            content=resultado_extraccion["content"],
            page_count=resultado_extraccion["page_count"],
            summary=None,
            summary_error=resultado_resumen["error"]
        )

    logger.info(f"Extracción + resumen exitoso - {duration}ms")
    return ExtractAndSummarizeResponse(
        content=resultado_extraccion["content"],
        page_count=resultado_extraccion["page_count"],
        summary=resultado_resumen.get("summary")
    )