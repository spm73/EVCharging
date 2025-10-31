param(
    [Parameter(Mandatory = $true)]
    [string]$KafkaIP
)

# Puerto fijo
$KafkaPort = 9092

# Lista de topics a crear
$topics = @(
    "supply-req",
    "supply-res",
    "supply-data",
    "supply-data2",
    "supply-error",
    "central-directives"
)

Write-Host "Creando topics en Kafka ($KafkaIP:$KafkaPort)..." -ForegroundColor Cyan

foreach ($topic in $topics) {
    Write-Host "→ Creando topic: $topic" -ForegroundColor Yellow

    kafka-topics.sh --create `
        --topic $topic `
        --bootstrap-server "$KafkaIP`:$KafkaPort"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✔ Topic '$topic' creado correctamente." -ForegroundColor Green
    } else {
        Write-Host "⚠ Error al crear topic '$topic' (puede que ya exista)." -ForegroundColor Red
    }
}

Write-Host "✅ Proceso finalizado." -ForegroundColor Cyan
