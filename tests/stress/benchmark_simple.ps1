# Benchmark simple con peticiones concurrentes usando PowerShell
# Útil para pruebas rápidas sin instalar k6 o Vegeta

param(
    [int]$TotalRequests = 100,
    [int]$ConcurrentRequests = 10,
    [string]$Url = "http://localhost:8001/extract",
    [string]$PdfPath = "$PSScriptRoot\pdfs\liviano.pdf"
)

Write-Host "=== Benchmark Simple ===" -ForegroundColor Cyan
Write-Host "Total peticiones: $TotalRequests" -ForegroundColor Yellow
Write-Host "Concurrencia: $ConcurrentRequests" -ForegroundColor Yellow
Write-Host "URL: $Url" -ForegroundColor Yellow
Write-Host "PDF: $PdfPath" -ForegroundColor Yellow
Write-Host ""

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$exitosos = 0
$fallidos = 0
$tiempos = @()

$batches = [math]::Ceiling($TotalRequests / $ConcurrentRequests)

for ($batch = 0; $batch -lt $batches; $batch++) {
    $jobs = @()
    $batchSize = [math]::Min($ConcurrentRequests, $TotalRequests - ($batch * $ConcurrentRequests))

    for ($i = 0; $i -lt $batchSize; $i++) {
        $jobs += Start-Job -ScriptBlock {
            param($url, $pdfPath)
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            try {
                $response = curl.exe -s -o NUL -w "%{http_code}" -X POST -F "file=@$pdfPath" $url
                $sw.Stop()
                return @{ status = $response; time = $sw.ElapsedMilliseconds }
            } catch {
                $sw.Stop()
                return @{ status = "error"; time = $sw.ElapsedMilliseconds }
            }
        } -ArgumentList $Url, $PdfPath
    }

    $results = $jobs | Wait-Job | Receive-Job
    $jobs | Remove-Job

    foreach ($r in $results) {
        if ($r.status -eq "200") {
            $exitosos++
        } else {
            $fallidos++
        }
        $tiempos += $r.time
    }

    $progress = [math]::Round((($batch + 1) * $ConcurrentRequests / $TotalRequests) * 100, 0)
    Write-Host "Progreso: $progress% ($exitosos exitosos, $fallidos fallidos)" -ForegroundColor Gray
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