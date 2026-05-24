from threading import Lock

class RegistryKey:
    _instance = None
    _instance_lock = Lock()
    
    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if hasattr(self, '_initialized'):
            return
        self.__key = self.__read_secret_key('registry_key')
        self._initialized = True
    
    def get_key(self) -> str:
        return self.__key
    
    @staticmethod
    def __read_secret_key(name: str) -> str:
        with open(f'/run/secrets/{name}', 'r') as f:
            return f.read().strip()
    