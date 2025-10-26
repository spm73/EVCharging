from cp_status import CPStatus
from cp_id import CPId

class EngineData:
    def __init__(self, location: str):
        self.location = location
        self.status = CPStatus()
        self.id = CPId()
        self.price = 0