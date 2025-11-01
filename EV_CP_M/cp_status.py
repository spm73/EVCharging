from enum import Enum

class CPStatusOptions(Enum):
    ACTIVE = 1
    SUPPLYING = 2
    STOPPED = 3
    WAITING_FOR_SUPPLY = 4
    BROKEN_DOWN = 5
    
class CPStatus:
    def __init__(self):
        self.status = CPStatusOptions.BROKEN_DOWN
        
    # def __init__(self, status_number: int):
    #     self.status = CPStatusOptions(status_number)
        
    def get_status(self) -> int:
        return self.status.value
    
    def set_active(self):
        self.status = CPStatusOptions.ACTIVE
        
    def set_supplying(self):
        self.status = CPStatusOptions.SUPPLYING
        
    def set_stopped(self):
        self.status = CPStatusOptions.STOPPED
        
    def set_waiting_for_supplying(self):
        self.status = CPStatusOptions.WAITING_FOR_SUPPLY
        
    def set_broken_down(self):
        self.status = CPStatusOptions.BROKEN_DOWN
        
    def is_active(self) -> bool:
        return self.status == CPStatusOptions.ACTIVE
        
    def is_supplying(self) -> bool:
        return self.status == CPStatusOptions.SUPPLYING
        
    def is_stopped(self) -> bool:
        return self.status == CPStatusOptions.STOPPED

    def is_waiting_for_supply(self):
        return self.status == CPStatusOptions.WAITING_FOR_SUPPLY
        
    def is_broken_down(self) -> bool:
        return self.status == CPStatusOptions.BROKEN_DOWN