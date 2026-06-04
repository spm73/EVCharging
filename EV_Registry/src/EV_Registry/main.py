from fastapi import FastAPI
from uvicorn import run
from os import getenv

from EV_Registry.routes import router

def main():
    app = FastAPI()
    app.include_router(router)
    
    run(
        "EV_Registry.main:app",
        host="0.0.0.0",
        port=int(getenv('API_PORT')),
        ssl_keyfile='/certs/server.key',
        ssl_certfile='/certs/server.crt'
    )


if __name__ == "__main__":
    main()
