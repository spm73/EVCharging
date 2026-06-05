from fastapi import FastAPI
from uvicorn import run
from os import getenv

from EV_Registry.routes import router
from EV_Registry.models import Base
from EV_Registry.database import engine

def main():
    print("[Main] Initializing registry database tables...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[Error] Failed to create tables: {e}")

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
