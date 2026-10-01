import io
import pdfplumber


def extraer_texto(contenido: bytes) -> dict:
    """Extrae texto de un PDF y devuelve el contenido y la cantidad de páginas."""
    texto_completo = ""
    cantidad_paginas = 0

    with pdfplumber.open(io.BytesIO(contenido)) as pdf:
        cantidad_paginas = len(pdf.pages)
        for pagina in pdf.pages:
            texto_extraido = pagina.extract_text()
            if texto_extraido:
                texto_completo += texto_extraido + "\n"

    return {
        "content": texto_completo.strip(),
        "page_count": cantidad_paginas
    }