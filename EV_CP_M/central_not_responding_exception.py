class CentralNotRespondingException(Exception):
    def __init__(self):
        super().__init__('Central stoped responding')