from enum import Enum

class CPStatus(Enum):
    ACTIVE = 1
    SUPPLYING = 2
    STOPPED = 3
    BROKEN_DOWN = 4