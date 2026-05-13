from cryptography.fernet import Fernet
from decimal import Decimal

from ..models.CPStatus import CPStatus
from .ActiveSupply import ActiveSupply

class CPInfo:
    def __init__(self, id: str) -> None:
        self.__id = id
        self.__temperature = 0.0
        self.__status = CPStatus.DISCONNECTED
        self.__key = None
        self.__active_supply: ActiveSupply | None = None
        
    def get_id(self) -> str:
        return self.__id
        
    def change_status(self, status: CPStatus) -> None:
        self.__status = status
        
    def get_status(self) -> CPStatus:
        return self.__status
    
    def get_temp(self) -> float:
        return self.__temperature
    
    def set_temperature(self, temperature: float) -> None:
        self.__temperature = temperature
    
    def assign_key(self) -> None:
        self.__key = Fernet.generate_key()
    
    def get_key(self) -> bytes | None:
        return self.__key
    
    def is_available(self) -> bool:
        return self.__status == CPStatus.ACTIVE
    
    def is_supplying(self) -> bool:
        return self.__active_supply is not None
    
    def start_supply(self, supply_id: int, driver_id: str | None) -> None:
        self.__active_supply = ActiveSupply(supply_id, driver_id)
    
    def update_supply(self, consumption: int, price: Decimal) -> None:
        if self.__active_supply is not None:
            self.__active_supply.update_data(consumption, price)
    
    def end_supply(self) -> None:
        self.__active_supply = None
    
    def get_active_supply(self) -> ActiveSupply | None:
        return self.__active_supply