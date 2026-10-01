import time
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"         # Funcionando normal
    OPEN = "open"             # Circuito abierto, rechaza peticiones
    HALF_OPEN = "half_open"   # Probando si se recuperó


class CircuitBreaker:
    """
    Implementación del patrón Circuit Breaker.

    - CLOSED: las peticiones pasan normalmente
    - OPEN: después de `failure_threshold` fallas consecutivas, se abre
    - HALF_OPEN: después de `recovery_timeout` segundos, permite 1 petición de prueba

    Propiedades configurables (según material del profesor):
    - failure_threshold: Cantidad de fallas que provocan apertura del circuito
    - recovery_timeout: Tiempo que permanece abierto antes de intentar nuevas invocaciones
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            # Verificar si ya pasó el tiempo de recuperación
            if self._last_failure_time and (time.time() - self._last_failure_time) >= self.recovery_timeout:
                logger.info(f"[CircuitBreaker:{self.name}] Transición OPEN → HALF_OPEN")
                self._state = CircuitState.HALF_OPEN
        return self._state

    def can_execute(self) -> bool:
        """Determina si se puede ejecutar la petición."""
        current_state = self.state
        if current_state == CircuitState.CLOSED:
            return True
        elif current_state == CircuitState.HALF_OPEN:
            return True  # Permite 1 petición de prueba
        else:  # OPEN
            return False

    def record_success(self):
        """Registra una petición exitosa."""
        if self._state == CircuitState.HALF_OPEN:
            logger.info(f"[CircuitBreaker:{self.name}] Transición HALF_OPEN → CLOSED")
        self._state = CircuitState.CLOSED
        self._failure_count = 0

    def record_failure(self):
        """Registra una petición fallida."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            logger.info(f"[CircuitBreaker:{self.name}] Falla en HALF_OPEN → OPEN")
            self._state = CircuitState.OPEN
            return

        if self._failure_count >= self.failure_threshold:
            logger.warning(
                f"[CircuitBreaker:{self.name}] Umbral alcanzado ({self._failure_count} fallas). "
                f"Transición → OPEN"
            )
            self._state = CircuitState.OPEN

    def reset(self):
        """Resetea el circuit breaker (para tests)."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
