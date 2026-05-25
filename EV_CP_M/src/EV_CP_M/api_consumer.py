import requests
from base64 import b64encode
from os import getenv

# Certificados del CP (el monitor los tiene en disco)
CLIENT_CERT = ("certs/cp.crt", "certs/cp.key")  # (cert, clave privada)

# CA que firmó el certificado del servidor del Registry
CA_CERT = "certs/ca.crt"

def register(cp_id: str, location: str) -> str:
    registry_host = getenv('REGISTRY_HOST')
    registry_port = int(getenv('REGISTRY_PORT'))
    registry_url = f"https://{registry_host}:{registry_port}"
    
    with open("certs/cp.crt") as f:
        certificate_pem = b64encode(f.read())

    response = requests.post(
        f"{registry_url}/registry/cp",
        json={
            "cp_id":       cp_id,
            "location":    location,
            "certificate": certificate_pem,
        },
        verify=CA_CERT,    # confía en la CA del servidor
        cert=CLIENT_CERT,  # presenta el certificado del CP
    )
    response.raise_for_status()
    return response.json()["token"]


def unregister(cp_id: str) -> None:
    registry_host = getenv('REGISTRY_HOST')
    registry_port = int(getenv('REGISTRY_PORT'))
    registry_url = f"https://{registry_host}:{registry_port}"
    
    requests.delete(
        f"{registry_url}/registry/cp/{cp_id}",
        verify=CA_CERT,
        cert=CLIENT_CERT,
    )