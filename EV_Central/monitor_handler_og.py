from json import loads, dumps
from typing import Literal
import sqlite3
from random import random

from stx_etx_connection import STXETXConnection
from connection_closed_exception import ConnectionClosedException
from closing_connection_exception import ClosingConnectionException
from cp_status import CPStatus

def monitor_handler(monitor_connection: STXETXConnection, status: CPStatus):
    try:
        monitor_connection.enq_answer()
    except ConnectionClosedException:
        status.set_disconnected()
        return
    
    running = True
    while running:
        try:
            petition = loads(monitor_connection.recv_message())
            msg_type = petition['type']
            if msg_type == 'auth':
                auth_result, price = authorize(petition['cp_id'])
                answer = {
                    'status': auth_result
                }
                if price:
                    answer['price'] = price
                monitor_connection.send_message(dumps(answer))
            elif msg_type == 'register':
                register_result, price = register(petition['cp_id'], petition['location'])
                answer = {
                    'status': register_result
                }
                if price:
                    answer['price'] = price
                monitor_connection.send_message(dumps(answer))
            elif msg_type == 'status':
                match petition['status']:
                    case 1:
                        status.set_active()
                    case 2:
                        status.set_supplying()
                    case 3:
                        status.set_stopped()
                    case 4:
                        status.set_waiting_for_supplying()
                    case 5:
                        status.set_broken_down()
                    case _:
                        status.set_disconnected()
                answer = {
                    'status': status.get_status()
                }
                monitor_connection.send_message(dumps(answer))
        except ClosingConnectionException:
            status.set_disconnected()
            running = False
            monitor_connection.close()
        except ConnectionClosedException:
            status.set_disconnected()
            return

        
def register(cp_id: str, location: str) -> tuple[Literal['registered', 'error'], float | None]:
    conexion = sqlite3.connect("/data/Charging_point.db")
    cursor = conexion.cursor()
    price = random()
    status = CPStatus()
    values = (cp_id, location, price, status)
    cursor.execute(f"INSERT INTO CP (id, location, price, status) VALUES (?, ?, ?, ?)", values)
    conexion.commit()
    conexion.close()


def authorize(cp_id: str) -> tuple[Literal['authorized', 'denied'], float | None]:
    conexion = sqlite3.connect("/data/Charging_point.db")
    cursor = conexion.cursor()
    cursor.execute(f"SELECT * FROM CP WHERE id = {cp_id}")
    cp_registers = cursor.fetchall()
    conexion.commit()
    conexion.close()
    if len(cp_registers) == 1:
        return ('authorized', cp_registers[0][2])
    else:
        return ('denied', None)
    
    # falta juntar esto con la interfaz gráfica