# Benchmark simple con peticiones concurrentes usando PowerShell
# Simplificado para evitar problemas de scopes con Start-Job

param(
    [int]$TotalRequests = 50,
    [string]$Url = "http://localhost:8001/extract",
    [string]$PdfPath = ""
)

if ($PdfPath -eq "") {
    $PdfPath = Join-Path $PSScriptRoot "pdfs\liviano.pdf"
} else {
    $PdfPath = (Resolve-Path $PdfPath).Path
}

Write-Host "=== Benchmark Simple (Secuencial Rápido) ===" -ForegroundColor Cyan
Write-Host "Total peticiones: $TotalRequests" -ForegroundColor Yellow
Write-Host "URL: $Url" -ForegroundColor Yellow
Write-Host "PDF: $PdfPath" -ForegroundColor Yellow
Write-Host ""

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$exitosos = 0
$fallidos = 0
$tiempos = [System.Collections.Generic.List[double]]::new()

for ($i = 0; $i -lt $TotalRequests; $i++) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        # Ejecutar curl
        $output = curl.exe -s -o NUL -w "%{http_code}" -X POST -F "file=@$PdfPath" $Url
        $sw.Stop()
        
        if ($output -eq "200") {
            $exitosos++
        } else {
            $fallidos++
            Write-Host "Falla HTTP: $output" -ForegroundColor Red
        }
    } catch {
        $sw.Stop()
        $fallidos++
        Write-Host "Error ejecución: $_" -ForegroundColor Red
    }
    
    $tiempos.Add($sw.ElapsedMilliseconds)
    
    # Progreso cada 10 peticiones
    if (($i + 1) % 10 -eq 0) {
        $progress = [math]::Round((($i + 1) / $TotalRequests) * 100, 0)
        Write-Host "Progreso: $progress% ($exitosos exitosos, $fallidos fallidos)" -ForegroundColor Gray
    }
}

$stopwatch.Stop()

$sortedTiempos = $tiempos | Sort-Object
$p50Index = [math]::Floor($sortedTiempos.Count * 0.5)
$p90Index = [math]::Floor($sortedTiempos.Count * 0.9)
$p95Index = [math]::Floor($sortedTiempos.Count * 0.95)

Write-Host ""
Write-Host "=== RESULTADOS ===" -ForegroundColor Green
Write-Host "Tiempo total: $([math]::Round($stopwatch.Elapsed.TotalSeconds, 2))s"
Write-Host "Peticiones exitosas: $exitosos / $TotalRequests ($([math]::Round($exitosos/$TotalRequests*100, 1))%)"
Write-Host "Peticiones fallidas: $fallidos"
Write-Host "Throughput: $([math]::Round($exitosos / $stopwatch.Elapsed.TotalSeconds, 2)) req/s"
Write-Host ""
Write-Host "=== LATENCIAS ===" -ForegroundColor Green
Write-Host "Mediana (P50): $($sortedTiempos[$p50Index])ms"
Write-Host "P90: $($sortedTiempos[$p90Index])ms"
Write-Host "P95: $($sortedTiempos[$p95Index])ms"
Write-Host "Máxima: $($sortedTiempos[-1])ms"
Write-Host "Mínima: $($sortedTiempos[0])ms"