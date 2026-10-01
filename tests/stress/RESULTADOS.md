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

## Nuestros Resultados

### Configuración
- Librería de extracción: PyMuPDF (fitz)
- Workers por réplica: 4
- Réplicas: (anotar)
- Límites: 1.0 CPU, 512M RAM por réplica
- Backpressure: semáforo con límite de 10 extracciones concurrentes

### Benchmark Simple (PowerShell)
- Fecha: 01/10/2026
- Total peticiones: 50
- Throughput: 5.64 req/s
- Latencia P50: 84 ms
- Latencia P90: 96 ms

### k6 Spike Test (cuando se instale k6)
- (completar)

### Vegeta Carga Fija (cuando se instale Vegeta)
- (completar)

## Notas de Optimización
- (anotar qué cambios se probaron y qué efecto tuvieron)