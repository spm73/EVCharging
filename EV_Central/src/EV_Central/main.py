import threading
import uvicorn
from fastapi import FastAPI

from EV_Central.api.cps import router as cp_router
from EV_Central.api.events import router as event_router
from EV_Central.api.drivers import router as driver_router
from EV_Central.api.transactions import router as transaction_router

app = FastAPI()
app.include_router(cp_router)
app.include_router(event_router)
app.include_router(driver_router)
app.include_router(transaction_router)

def start_api() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
def main():
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()


if __name__ == "__main__":
    main()
