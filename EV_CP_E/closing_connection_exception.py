class ClosingConnectionException(Exception):
    def __init__(self):
        super().__init__('Peer requested closing the connection')