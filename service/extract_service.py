import io
import fitz  # pymupdf


def extraer_texto(contenido: bytes) -> dict:
    """Extrae texto de un PDF usando PyMuPDF (más rápido que pdfplumber para alto rendimiento)."""
    texto_completo = ""
    cantidad_paginas = 0

    with fitz.open(stream=contenido, filetype="pdf") as pdf:
        cantidad_paginas = len(pdf)
        for pagina in pdf:
            texto_extraido = pagina.get_text()
            if texto_extraido:
                texto_completo += texto_extraido + "\n"

    return {
        "content": texto_completo.strip(),
        "page_count": cantidad_paginas
    }