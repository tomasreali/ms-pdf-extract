import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ===== Tests del Health Check (Tarea 8) =====

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ms-pdf-extract"
    assert "version" in data
    assert "uptime_seconds" in data
    assert "timestamp" in data


# ===== Tests de POST /extract (Tareas 1-4, existentes) =====

def test_extract_pdf_exitoso():
    with open("tests/dummy.pdf", "rb") as f:
        contenido_pdf = f.read()

    response = client.post(
        "/extract",
        files={"file": ("dummy.pdf", contenido_pdf, "application/pdf")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "page_count" in data
    assert isinstance(data["page_count"], int)
    assert data["page_count"] > 0


def test_extract_archivo_no_pdf():
    contenido_falso = b"esto no es un pdf"
    response = client.post(
        "/extract",
        files={"file": ("archivo.txt", contenido_falso, "text/plain")}
    )
    assert response.status_code == 400


def test_extract_archivo_muy_grande():
    contenido_pesado = b"0" * (11 * 1024 * 1024)  # 11 MB
    response = client.post(
        "/extract",
        files={"file": ("pesado.pdf", contenido_pesado, "application/pdf")}
    )
    assert response.status_code == 400
    assert "demasiado grande" in response.json()["detail"]


# ===== Tests de POST /extract-and-summarize (Tarea 6) =====

def test_extract_and_summarize_exitoso(mocker):
    """Test del flujo completo: extracción + resumen"""
    # Mock del servicio de extracción
    mocker.patch(
        "app.routers.extraer_texto",
        return_value={"content": "Texto extraído del PDF de prueba", "page_count": 3}
    )
    # Mock del cliente HTTP hacia ms-ia-summary
    mocker.patch(
        "app.routers.solicitar_resumen",
        new_callable=AsyncMock,
        return_value={"summary": "Resumen generado por IA"}
    )

    response = client.post(
        "/extract-and-summarize",
        files={"file": ("test.pdf", b"%PDF-contenido", "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Texto extraído del PDF de prueba"
    assert data["page_count"] == 3
    assert data["summary"] == "Resumen generado por IA"
    assert data["summary_error"] is None


def test_extract_and_summarize_ia_caida(mocker):
    """Test de degradación elegante cuando ms-ia-summary no responde"""
    mocker.patch(
        "app.routers.extraer_texto",
        return_value={"content": "Texto extraído del PDF de prueba", "page_count": 2}
    )
    mocker.patch(
        "app.routers.solicitar_resumen",
        new_callable=AsyncMock,
        return_value={"error": "Servicio de resumen no disponible después de 3 reintentos: Connection refused"}
    )

    response = client.post(
        "/extract-and-summarize",
        files={"file": ("test.pdf", b"%PDF-contenido", "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Texto extraído del PDF de prueba"
    assert data["summary"] is None
    assert data["summary_error"] is not None
    assert "no disponible" in data["summary_error"]


def test_extract_and_summarize_archivo_no_pdf():
    """Validación: rechaza archivos que no son PDF"""
    response = client.post(
        "/extract-and-summarize",
        files={"file": ("archivo.txt", b"esto no es un pdf", "text/plain")}
    )
    assert response.status_code == 400


def test_extract_and_summarize_archivo_muy_grande():
    """Validación: rechaza archivos que superan el límite de tamaño"""
    contenido_pesado = b"0" * (11 * 1024 * 1024)  # 11 MB
    response = client.post(
        "/extract-and-summarize",
        files={"file": ("pesado.pdf", contenido_pesado, "application/pdf")}
    )
    assert response.status_code == 400