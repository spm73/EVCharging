from cryptography.fernet import Fernet

from ..models.CPStatus import CPStatus

class CPInfo:
    def __init__(self, id: str) -> None:
        self.__id = id
        self.__status = CPStatus.DISCONNECTED
        self.__key = None
        
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