import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ms-pdf-extract"


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