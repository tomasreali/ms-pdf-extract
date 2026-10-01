import httpx
import asyncio
import logging
from config.settings import settings
from service.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

# Instancia global del Circuit Breaker para ms-ia-summary
summary_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30,
    name="ms-ia-summary"
)


async def solicitar_resumen(texto: str) -> dict:
    """
    Llama al microservicio ms-ia-summary para obtener un resumen.
    Implementa degradación elegante: si falla, devuelve error dict.

    Incluye:
    - Retry con backoff exponencial (máx 3 reintentos)
    - Circuit Breaker (5 fallas → abierto, 30s recovery, half-open 1 petición)
    """
    return await _solicitar_con_retry_y_circuit_breaker(texto)


async def _solicitar_con_retry_y_circuit_breaker(
    texto: str,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> dict:
    """
    Llama a ms-ia-summary con Retry (backoff exponencial) y Circuit Breaker.

    - Si el circuit breaker está abierto → respuesta degradada inmediata
    - Si falla → reintenta hasta max_retries veces con backoff exponencial
    - Si todas las llamadas fallan → registra falla en circuit breaker
    """

    # 1. Verificar Circuit Breaker
    if not summary_circuit_breaker.can_execute():
        logger.warning("[SummaryClient] Circuit breaker ABIERTO. Respuesta degradada.")
        return {"error": "Circuit breaker abierto. Servicio de resumen no disponible."}

    # 2. Intentar con Retry + Backoff Exponencial
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[SummaryClient] Intento {attempt}/{max_retries} a ms-ia-summary")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    settings.summary_service_url,
                    json={"text": texto}
                )
                response.raise_for_status()

                # Éxito → registrar en circuit breaker
                summary_circuit_breaker.record_success()
                logger.info("[SummaryClient] Resumen obtenido exitosamente")
                return response.json()

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            last_error = e
            logger.warning(f"[SummaryClient] Intento {attempt} falló: {e}")

            if attempt < max_retries:
                delay = base_delay * (2 ** (attempt - 1))  # 1s, 2s, 4s
                logger.info(f"[SummaryClient] Esperando {delay}s antes del reintento...")
                await asyncio.sleep(delay)

    # 3. Todos los reintentos fallaron → registrar falla en circuit breaker
    summary_circuit_breaker.record_failure()
    logger.error(f"[SummaryClient] Todos los reintentos agotados. Último error: {last_error}")
    return {"error": f"Servicio de resumen no disponible después de {max_retries} reintentos: {last_error}"}
