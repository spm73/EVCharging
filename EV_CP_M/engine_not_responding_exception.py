class EngineNotRespondingException(Exception):
    def __init__(self):
        super().__init__('Engine stoped responding')