from threading import Timer, Lock
from sqlalchemy import select
from sqlalchemy.orm import Session

from .CPInfo import CPInfo
from .Database import Database
from ..models.CP import CP
from ..models.Supply import Supply
from ..models.CPStatus import CPStatus

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
        self.__engine = Database().get_engine()
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
    
    def get_active_cps_ids(self) -> list[str]:
        return [id for id, cp in self.__cps.items() if cp.get_status() == CPStatus.ACTIVE]
        
    def add_cp(self, cp_id: str) -> CPInfo:
        with self.__lock:
            self.__cps[cp_id] = CPInfo(cp_id)
        return self.__cps[cp_id]
            
    def get_cp_by_supply_id(self, supply_id: int) -> CPInfo | None:
        with self.__lock:
            for cp in self.__cps.values():
                supply = cp.get_active_supply()
                if supply and supply.id == supply_id:
                    return cp
        return None
    
    def end_supply(self, cp_id: str) -> None:
        with self.__lock:
            cp = self.__cps.get(cp_id)
            if cp is None:
                raise KeyError(f'CP ID: {cp_id} is not registered')
            active_supply = cp.get_active_supply()
            if active_supply is None:
                return
            cp.end_supply()
        
        with Session(Database().get_engine()) as session:
            supply = session.get(Supply, active_supply.id)
            if supply is not None:
                supply.is_done = True
                supply.consumption = active_supply.consumption
                supply.price = active_supply.price
                session.commit()
        
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
