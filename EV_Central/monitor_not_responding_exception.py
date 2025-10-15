class MonitorNotRespondingException(Exception):
    def __init__(self):
        super().__init__('Monitor stoped responding')