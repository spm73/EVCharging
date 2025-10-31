@echo off
setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Uso: create_kafka_topics.bat ^<KAFKA_IP^>
    exit /b 1
)

set KAFKA_IP=%1
set KAFKA_PORT=9092

set TOPICS=supply-req supply-res supply-data supply-data2 supply-error central-directives

echo Creando topics en Kafka %KAFKA_IP%:%KAFKA_PORT%...
for %%T in (%TOPICS%) do (
    echo Creando topic: %%T
    kafka-topics.bat --create --topic %%T --bootstrap-server %KAFKA_IP%:%KAFKA_PORT%
    if !errorlevel! == 0 (
        echo Topic %%T creado correctamente.
    ) else (
        echo Error al crear %%T (puede que ya exista).
    )
)

echo.
echo ✅ Proceso finalizado.
