# Script maestro para ejecutar todas las pruebas de carga
# Uso: powershell -File tests\stress\run_benchmarks.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SUITE DE PRUEBAS DE CARGA - ms-pdf-extract" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar que el servicio esté corriendo
Write-Host "[1/4] Verificando que el servicio esté disponible..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method GET -TimeoutSec 5
    Write-Host "  Servicio OK: $($health.service) v$($health.version)" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: El servicio no está corriendo en localhost:8001" -ForegroundColor Red
    Write-Host "  Ejecutá primero: docker compose up --build -d" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 2. Verificar PDFs de prueba
Write-Host "[2/4] Verificando PDFs de prueba..." -ForegroundColor Yellow
$pdfDir = "$PSScriptRoot\pdfs"
$pdfs = Get-ChildItem -Path $pdfDir -Filter "*.pdf" -ErrorAction SilentlyContinue
if ($pdfs.Count -eq 0) {
    Write-Host "  ERROR: No hay PDFs en $pdfDir" -ForegroundColor Red
    exit 1
}
foreach ($pdf in $pdfs) {
    Write-Host "  - $($pdf.Name) ($([math]::Round($pdf.Length / 1KB, 1)) KB)" -ForegroundColor Gray
}

Write-Host ""

# 3. Ejecutar benchmark simple
Write-Host "[3/4] Ejecutando benchmark simple (50 peticiones, concurrencia 5)..." -ForegroundColor Yellow
Write-Host ""
& "$PSScriptRoot\benchmark_simple.ps1" -TotalRequests 50 -ConcurrentRequests 5

Write-Host ""

# 4. Si k6 está instalado, ejecutar spike test
Write-Host "[4/4] Verificando si k6 está disponible..." -ForegroundColor Yellow
$k6Available = Get-Command k6 -ErrorAction SilentlyContinue
if ($k6Available) {
    Write-Host "  k6 encontrado. Ejecutando spike test..." -ForegroundColor Green
    k6 run "$PSScriptRoot\spike_test.js"
} else {
    Write-Host "  k6 no está instalado. Saltando spike test." -ForegroundColor Gray
    Write-Host "  Para instalar: winget install Grafana.k6" -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  PRUEBAS COMPLETADAS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan