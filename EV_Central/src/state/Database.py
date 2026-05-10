from sqlalchemy import create_engine, Engine, URL
from threading import Lock
from os import getenv

class Database:
    _instance = None
    _instance_lock = Lock()
    
    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        url = URL.create(
            drivername=f'{getenv("DB_CONNECTION")}+{getenv("DB_DRIVER")}',
            username=getenv("DB_USERNAME"),
            password=getenv("DB_PASSWORD"),
            host=getenv("DB_HOST"),
            port=int(getenv("DB_PORT")),
            database=getenv("DB_NAME")
        )
        self.__engine = create_engine(url)
        self._initialized = True
    
    def get_engine(self) -> Engine:
        return self.__engine