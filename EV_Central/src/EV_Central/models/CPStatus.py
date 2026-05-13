from enum import Enum

class CPStatus(Enum):
    ACTIVE = 'Active'
    STOPPED = 'Stopped'
    SUPPLYING = 'Supplying'
    BROKEN_DOWN = 'Broken Down'
    DISCONNECTED = 'Disconnected'