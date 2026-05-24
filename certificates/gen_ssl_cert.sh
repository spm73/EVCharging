#!/bin/bash

# ==========================================================
# Script Automático para Certificados SSL (Clásico - Sin SAN)
# ==========================================================

# 1. Comprobar si existe la Autoridad Certificadora (CA) y crearla si no existe
if [ ! -f "ca.key" ] || [ ! -f "ca.crt" ]; then
    echo "🛠️ No se encontró una CA. Creando una nueva CA Local..."
    openssl genrsa -out ca.key 2048
    openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt -subj "/C=ES/ST=Local/L=Local/O=Mi Autoridad Local/CN=Mi CA Local"
    echo "✅ CA Local creada con éxito."
    echo "---------------------------------------------------"
fi

# 2. Pedir datos al usuario
echo "🔐 Generador de Certificados Únicos"
read -p "👉 Introduce la dirección exacta (Common Name) (ej: 192.168.1.50 o localhost): " HOST_ADDR

# 3. Generar la Clave del Servidor
echo "⚙️ Generando clave privada para server..."
openssl genrsa -out server.key 2048

# 4. Generar el CSR (Petición) inyectando el Common Name directamente
echo "📝 Creando petición de firma..."
openssl req -new -key server.key -out server.csr -subj "/C=ES/ST=Alicante/L=Alicante/O=sd-practice/OU=recovery/CN=$HOST_ADDR/emailAddress=spm119@alu.ua.es"

# 5. Firmar el certificado usando la CA
echo "✍️ Firmando certificado con la CA..."
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256

# 6. Limpiar el archivo temporal
rm server.csr

echo "---------------------------------------------------"
echo "🎉 ¡PROCESO COMPLETADO!"
echo "Tu certificado exclusivo para '$HOST_ADDR' está listo:"
echo " 🔑 Clave Privada: server.key"
echo " 📜 Certificado:   server.crt"
