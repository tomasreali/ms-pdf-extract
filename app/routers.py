from fastapi import APIRouter, UploadFile, File, HTTPException
import logging
from config.settings import settings
from service.extract_service import extraer_texto
from app.models.extract_response import ExtractResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name}


@router.post("/extract", response_model=ExtractResponse)
async def extract_text(file: UploadFile = File(...)):
    logger.info(f"Recibiendo archivo: {file.filename}")

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

    logger.info(f"Extracción exitosa: {resultado['page_count']} páginas")
    return resultado