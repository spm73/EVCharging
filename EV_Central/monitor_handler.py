from json import loads, dumps
from typing import Literal

from stx_etx_connection import STXETXConnection
from connection_closed_exception import ConnectionClosedException
from closing_connection_exception import ClosingConnectionException
from cp_status import CPStatus

def monitor_handler(monitor_connection: STXETXConnection, status: CPStatus):
    try:
        monitor_connection.enq_answer()
    except ConnectionClosedException:
        status = CPStatus.DISCONNECTED
        return
    
    running = True
    while running:
        try:
            petition = loads(monitor_connection.recv_message())
            msg_type = petition['type']
            if msg_type == 'auth':
                auth_result = authorize(petition['cp_id'])
                answer = {
                    'status': auth_result
                }
                monitor_connection.send_message(dumps(answer))
            elif msg_type == 'register':
                register_result = register(petition['cp_id'], petition['location'])
                answer = {
                    'status': register_result
                }
                monitor_connection.send_message(dumps(answer))
            elif msg_type == 'status':
               status = petition['status']
               answer = {
                   'status': status
               }
               monitor_connection.send_message(dumps(answer))
        except ClosingConnectionException:
            status = CPStatus.DISCONNECTED
            running = False
            monitor_connection.close()
        except ConnectionClosedException:
            status = CPStatus.DISCONNECTED
            return


        
def register(cp_id: str, location: str) -> Literal['registered', 'error']:
    pass


def authorize(cp_id: str) -> Literal['authorized', 'denied']:
    pass