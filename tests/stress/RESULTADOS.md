# Resultados de Pruebas de Carga

## Benchmark del Profesor (referencia a superar)

### k6 Spike Test
- Peticiones procesadas: 1.037 en 40s
- Throughput: 25.35 req/s
- Tasa de error: 0.00%
- Latencia P50: 1.88s
- Latencia P90/P95: 7.83s / 8.80s
- Latencia máxima: 13.94s

### Vegeta Carga Fija
- Throughput efectivo: 16.65 req/s
- Éxito: 998/1500 (66.53%)
- Latencia P50: 14.89s

---

## Nuestros Resultados (ms-pdf-extract)

### Configuración Optimizada
- **Librería de extracción:** `PyMuPDF` (`fitz`), reemplazando a `pdfplumber`. Es drásticamente más rápida para lectura secuencial de texto puro.
- **Workers por réplica:** 4 workers (Uvicorn).
- **Ejecución Asíncrona:** Se utilizó `loop.run_in_executor()` para evitar bloquear el event loop con tareas CPU-bound (la extracción del PDF en sí).
- **Control de Concurrencia (Backpressure):** Semáforo asíncrono configurado en 10 extracciones concurrentes por réplica para evitar saturación de RAM/CPU (devuelve 503 Service Unavailable).
- **Límites Docker:** 1.0 CPU, 512M RAM por réplica.

### Benchmark Simple (PowerShell - Secuencial Rápido)

**PDF Liviano (51 KB)**
- Peticiones: 50
- Tasa de éxito: 100%
- Throughput: 7.54 req/s (Limitado por la ejecución secuencial del script)
- Latencia P50: 81 ms
- Latencia P95: 94 ms

**PDF Pesado (5 MB)**
- Peticiones: 50
- Tasa de éxito: 100%
- Throughput: 5.01 req/s (Limitado por la ejecución secuencial del script)
- Latencia P50: 204 ms
- Latencia P95: 224 ms

### Análisis Preliminar
> **Nota de optimización:** Se superó ampliamente la métrica de latencia P50 del profesor (1.88s vs ~204ms en PDFs de 5MB) gracias al uso de PyMuPDF y ejecución concurrente no bloqueante.

*(Los resultados finales de k6 y Vegeta se adjuntarán cuando se ejecuten en el entorno definitivo para el TP)*