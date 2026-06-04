#!/bin/bash

# ==========================================================
# Script Automático para Certificados de Charging Points (CP)
# ==========================================================

# 1. Comprobar si existe la CA
if [ ! -f "ca.key" ] || [ ! -f "ca.crt" ]; then
    echo "❌ ERROR: No se encontró la Autoridad Certificadora (ca.key y ca.crt)."
    echo "Por favor, ejecuta primero gen_ssl_cert.sh para generar la CA."
    exit 1
fi

# 2. Pedir el ID del CP
echo "🔐 Generador de Certificados para Charging Points"
read -p "👉 Introduce el identificador del CP (ej: CP01, CP02): " CP_ID

if [ -z "$CP_ID" ]; then
    echo "❌ El ID no puede estar vacío."
    exit 1
fi

PREFIX="cp_$CP_ID"

# 3. Generar la Clave Privada del CP
echo "⚙️ Generando clave privada para $CP_ID..."
openssl genrsa -out "${PREFIX}.key" 2048

# 4. Generar el CSR (Petición) inyectando el ID directamente en el Common Name
echo "📝 Creando petición de firma para $CP_ID..."
openssl req -new -key "${PREFIX}.key" -out "${PREFIX}.csr" -subj "/C=ES/ST=Alicante/L=Alicante/O=sd-practice/OU=recovery/CN=$CP_ID/emailAddress=spm119@alu.ua.es"

# 5. Firmar el certificado usando la CA
echo "✍️ Firmando certificado del CP con la CA..."
openssl x509 -req -in "${PREFIX}.csr" -CA ca.crt -CAkey ca.key -CAcreateserial -out "${PREFIX}.crt" -days 365 -sha256

# 6. Limpiar el archivo temporal
rm "${PREFIX}.csr"

echo "---------------------------------------------------"
echo "🎉 ¡PROCESO COMPLETADO!"
echo "Tu certificado exclusivo para el '$CP_ID' está listo:"
echo " 🔑 Clave Privada: ${PREFIX}.key"
echo " 📜 Certificado:   ${PREFIX}.crt"
echo ""
echo "💡 Recuerda: El monitor (EV_CP_M) espera que renombres estos archivos a 'cp.key' y 'cp.crt'"
echo "   y los coloques dentro de su carpeta 'certs/' para poder conectar con el Registry."
