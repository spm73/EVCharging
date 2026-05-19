from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import load_pem_x509_certificate
from base64 import b64decode
from jwt import encode
from datetime import datetime, timezone

CA_CERTIFICATE_PATH = "/certs/ca.crt"
JWT_ALGORITHM = "HS256"

def verify_certificate(cert_b64: str, expected_cp_id: str) -> bool:
    try:
        # Decodificar el certificado de base64 a PEM
        cert_pem = b64decode(cert_b64)
        cert = load_pem_x509_certificate(cert_pem)

        # Cargar tu CA
        with open(CA_CERTIFICATE_PATH, "rb") as f:
            ca_cert = load_pem_x509_certificate(f.read())

        # Verificar que el certificado está firmado por tu CA
        ca_cert.public_key().verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )

        # Verificar que el CN del certificado coincide con el cp_id
        cn = cert.subject.get_attributes_for_oid(
            x509.NameOID.COMMON_NAME
        )[0].value

        return cn == expected_cp_id

    except Exception:
        return False
    

def generate_jwt(cp_id: str) -> str:
    payload = {
        "sub": cp_id,
        "iat": datetime.now(timezone.utc) # issued at
        # Sin expiración fija, o puedes añadir "exp" si quieres que caduque
    }
    return encode(payload, "central_key", algorithm=JWT_ALGORITHM)