class ConnectionClosedException(Exception):
    def __init__(self):
        super().__init__('Connection has been closed abruptly')