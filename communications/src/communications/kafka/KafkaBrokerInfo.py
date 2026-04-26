class KafkaBrokerInfo:
    def __init__(self, ip_address: str, port_number: int) -> None:
        self.__ip = ip_address
        self.__port = port_number
        
    def get_ip(self) -> str: 
        return self.__ip
    
    def get_port(self) -> int:
        return self.__port
    
    def get_broker_endpoint(self) -> str:
        return f'{self.__ip}:{self.__port}'