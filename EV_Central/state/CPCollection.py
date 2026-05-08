from threading import Timer, Lock
from sqlalchemy import URL, create_engine, Engine, select
from sqlalchemy.orm import Session
from os import getenv

from .CPInfo import CPInfo
from ..models.CP import CP

class CPCollection:
    INTERVAL: float = 60.0
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
        self.__engine = CPCollection.__create_engine()
        self.__cps: dict[str, CPInfo] = {}
        self.__lock: Lock = Lock()
        self.__load_from_db()
        self.__timer: Timer = Timer(CPCollection.INTERVAL, self.__store_in_db)
        self.__timer.start()
        self._initialized = True
        
    def shutdown(self):
        self.__timer.cancel()
        self.__store_in_db()
        
    def get_cp(self, cp_id: str) -> CPInfo:
        cp = self.__cps.get(cp_id)
        if cp is None:
            raise KeyError(f'CP ID: {cp_id} is not registered')
        return cp
        
    def add_cp(self, cp_id: str) -> None:
        with self.__lock:
            self.__cps[cp_id] = CPInfo(cp_id)
        
    def __remove_cp(self, cp_id: str) -> None:
        with self.__lock:
            self.__cps.pop(cp_id)
            
    def __load_from_db(self):
        with Session(self.__engine) as session:
            cps = session.scalars(select(CP)).all()
            for cp in cps:
                self.add_cp(cp.id)
                self.__cps[cp.id].change_status(cp.status)        
        
    def __store_in_db(self):
        cps = None
        with self.__lock:
            cps = list(self.__cps.values())
        
        with Session(self.__engine) as session:    
            for cp in cps:
                cp_model = session.get(CP, cp.get_id())
                if cp_model is None:
                    self.__remove_cp(cp.get_id())
                    continue
                cp_model.status = cp.get_status()
            session.commit()
        
        self.__timer = Timer(CPCollection.INTERVAL, self.__store_in_db)
        self.__timer.start()
        
    @staticmethod
    def __create_engine() -> Engine:
        url = URL.create(
            drivername=f'{getenv('DB_CONNECTION')}+{getenv('DB_DRIVER')}',
            username=getenv('DB_USERNAME'),
            password=getenv('DB_PASSWORD'),
            host=getenv('DB_HOST'),
            port=int(getenv('DB_PORT')),
            database=getenv('DB_NAME')
        )
        return create_engine(url)