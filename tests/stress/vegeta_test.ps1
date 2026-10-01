# Script de prueba de carga con Vegeta
# Perfil: 50 req/s durante 30 segundos, timeout 30s

Write-Host "=== Test de Carga Fija con Vegeta ===" -ForegroundColor Cyan
Write-Host "Perfil: 50 req/s durante 30 segundos" -ForegroundColor Yellow
Write-Host ""

$PDF_DIR = "$PSScriptRoot\pdfs"
$TARGET_URL = "http://localhost:8001/extract"
$RATE = 50
$DURATION = "30s"
$TIMEOUT = "30s"

# Verificar que los PDFs existen
$pdfs = Get-ChildItem -Path $PDF_DIR -Filter "*.pdf"
if ($pdfs.Count -eq 0) {
    Write-Host "ERROR: No se encontraron PDFs en $PDF_DIR" -ForegroundColor Red
    exit 1
}

Write-Host "PDFs encontrados: $($pdfs.Count)" -ForegroundColor Green
foreach ($pdf in $pdfs) {
    Write-Host "  - $($pdf.Name) ($([math]::Round($pdf.Length / 1KB, 1)) KB)"
}

Write-Host ""
Write-Host "Ejecutando Vegeta..." -ForegroundColor Cyan

# Generar targets rotativos
$targetsFile = "$PSScriptRoot\targets.txt"
$targets = @()
foreach ($pdf in $pdfs) {
    $targets += "POST $TARGET_URL"
    $targets += "@$($pdf.FullName)"
    $targets += ""
}
$targets | Out-File -FilePath $targetsFile -Encoding UTF8

# Ejecutar vegeta
vegeta attack -targets=$targetsFile -rate=$RATE -duration=$DURATION -timeout=$TIMEOUT | vegeta report

Write-Host ""
Write-Host "Test completado." -ForegroundColor Green