from fastapi import FastAPI
from uvicorn import run
from os import getenv

from routes import router

def main():
    app = FastAPI()
    app.include_router(router)
    
    run(
        "main:app",
        host="0.0.0.0",
        port=int(getenv('API_PORT')),
        ssl_keyfile='/certs/server.key',
        ssl_certfile='/certs/server.crt'
    )


if __name__ == "__main__":
    main()
