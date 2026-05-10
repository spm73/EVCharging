from cryptography.fernet import Fernet
from decimal import Decimal

from ..models.CPStatus import CPStatus
from .ActiveSupply import ActiveSupply

class CPInfo:
    def __init__(self, id: str) -> None:
        self.__id = id
        self.__status = CPStatus.DISCONNECTED
        self.__key = None
        self.__active_supply: ActiveSupply | None = None
        
    def get_id(self) -> str:
        return self.__id
        
    def change_status(self, status: CPStatus) -> None:
        self.__status = status
        
    def get_status(self) -> CPStatus:
        return self.__status
    
    def assign_key(self) -> None:
        self.__key = Fernet.generate_key()
    
    def get_key(self) -> bytes | None:
        return self.__key
    
    def is_available(self) -> bool:
        return self.__status == CPStatus.ACTIVE
    
    def start_supply(self, supply_id: int) -> None:
        self.__active_supply = ActiveSupply(supply_id)
    
    def update_supply(self, consumption: int, price: Decimal) -> None:
        if self.__active_supply is not None:
            self.__active_supply.update_data(consumption, price)
    
    def end_supply(self) -> None:
        self.__active_supply = None
    
    def get_active_supply(self) -> ActiveSupply | None:
        return self.__active_supply