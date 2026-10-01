import time
import pytest
from service.circuit_breaker import CircuitBreaker, CircuitState


class TestCircuitBreaker:

    def setup_method(self):
        """Crear un CircuitBreaker con umbral bajo y timeout corto para tests rápidos."""
        self.cb = CircuitBreaker(failure_threshold=3, recovery_timeout=2, name="test")

    def test_estado_inicial_cerrado(self):
        """El circuit breaker arranca en estado CLOSED."""
        assert self.cb.state == CircuitState.CLOSED
        assert self.cb.can_execute() is True

    def test_se_abre_tras_umbral_de_fallas(self):
        """Después de 3 fallas consecutivas (umbral=3), el circuito se abre."""
        for _ in range(3):
            self.cb.record_failure()

        assert self.cb.state == CircuitState.OPEN
        assert self.cb.can_execute() is False

    def test_no_se_abre_con_menos_fallas_que_umbral(self):
        """Con 2 fallas (umbral=3), sigue cerrado."""
        self.cb.record_failure()
        self.cb.record_failure()

        assert self.cb.state == CircuitState.CLOSED
        assert self.cb.can_execute() is True

    def test_exito_resetea_contador_fallas(self):
        """Un éxito resetea el contador de fallas consecutivas."""
        self.cb.record_failure()
        self.cb.record_failure()
        self.cb.record_success()

        assert self.cb._failure_count == 0
        assert self.cb.state == CircuitState.CLOSED

    def test_transicion_open_a_half_open(self):
        """Después del timeout de recuperación, pasa de OPEN a HALF_OPEN."""
        for _ in range(3):
            self.cb.record_failure()

        assert self.cb.state == CircuitState.OPEN

        # Simular que pasó el tiempo de recuperación (2s < 3s)
        self.cb._last_failure_time = time.time() - 3

        assert self.cb.state == CircuitState.HALF_OPEN
        assert self.cb.can_execute() is True

    def test_half_open_exito_cierra_circuito(self):
        """En HALF_OPEN, un éxito cierra el circuito (vuelve a CLOSED)."""
        for _ in range(3):
            self.cb.record_failure()
        self.cb._last_failure_time = time.time() - 3

        assert self.cb.state == CircuitState.HALF_OPEN

        self.cb.record_success()
        assert self.cb.state == CircuitState.CLOSED
        assert self.cb.can_execute() is True

    def test_half_open_falla_abre_circuito(self):
        """En HALF_OPEN, una falla vuelve a abrir el circuito."""
        for _ in range(3):
            self.cb.record_failure()
        self.cb._last_failure_time = time.time() - 3

        # Trigger transición a HALF_OPEN
        _ = self.cb.state

        self.cb.record_failure()
        assert self.cb.state == CircuitState.OPEN
        assert self.cb.can_execute() is False

    def test_reset_vuelve_a_estado_inicial(self):
        """El método reset() devuelve todo al estado inicial."""
        for _ in range(3):
            self.cb.record_failure()
        assert self.cb.state == CircuitState.OPEN

        self.cb.reset()

        assert self.cb.state == CircuitState.CLOSED
        assert self.cb._failure_count == 0
        assert self.cb._last_failure_time is None
