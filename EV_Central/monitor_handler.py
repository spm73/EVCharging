from json import loads, dumps
from typing import Literal, Any
import sqlite3
from random import random
from queue import Queue
from stx_etx_connection import STXETXConnection
from connection_closed_exception import ConnectionClosedException
from closing_connection_exception import ClosingConnectionException
from cp_status import CPStatus

def monitor_handler(monitor_connection: STXETXConnection, queue: Queue):
    try:
        monitor_connection.enq_answer()
    except ConnectionClosedException:
        monitor_connection.close()
        return
    
    running = True
    cp_id = None
    while running:
        try:
            petition = loads(monitor_connection.recv_message())
            msg_type = petition['type']
            if msg_type == 'auth':
                result = authorize(petition['cp_id'])
                answer = {
                    'status': result['result']
                }
                if result.get('price'):
                    answer['price'] = result['price']
                monitor_connection.send_message(dumps(answer))
                if result.get('cp_id'):
                    cp_id = result.get('cp_id')
            elif msg_type == 'register':
                result = register(petition['cp_id'], petition['location'], queue)
                answer = {
                    'status': result['result']
                }
                if result.get('price'):
                    answer['price'] = result.get('price')
                monitor_connection.send_message(dumps(answer))
                if result.get('cp_id'):
                    cp_id = result.get('cp_id')
            elif msg_type == 'status':
                cpstatus = CPStatus()
                match petition['status']:
                    case 1:

                        data = {
                            'action': cpstatus.set_active(),
                            'cp_id': cp_id
                        }
                        queue.put(('health_status', data))
                    case 2:
                        data = {
                            'action': cpstatus.set_supplying(),
                            'cp_id': cp_id
                        }
                        queue.put(('health_status', data))
                    case 3:
                        data = {
                            'action': cpstatus.set_stopped(),
                            'cp_id': cp_id
                        }
                        queue.put(('health_status', data))
                    case 4:
                        data = {
                            'action': cpstatus.set_waiting_for_supplying(),
                            'cp_id': cp_id
                        }
                        queue.put(('health_status', data))
                    case 5:
                        data = {
                            'action': cpstatus.set_broken_down(),
                            'cp_id': cp_id
                        }
                        queue.put(('health_status', data))
                    case _:
                        data = {
                            'action': cpstatus.set_disconnected(),
                            'cp_id': cp_id
                        }
                        queue.put(('health_status', data))
                answer = {
                    'status': petition['status']
                }
                monitor_connection.send_message(dumps(answer))
        except ClosingConnectionException:
            data = {
                'action': 'set_disconnected',
                'cp_id': cp_id
            }
            queue.put(('health_status', data))
            running = False
            cp_id = None
            monitor_connection.close()
        except ConnectionClosedException:
            data = {
                'action': 'set_disconnected',
                'cp_id': cp_id
            }
            queue.put(('health_status', data))
            monitor_connection.close()
            return

        
def register(cp_id: str, location: str, queue: Queue) -> dict[str, Any]:
    conexion = sqlite3.connect("/data/Charging_point.db")
    cursor = conexion.cursor()
    price = random()
    status = CPStatus()
    values = (cp_id, location, price, status.get_status())
    
    try:
        cursor.execute(f"INSERT INTO CP (id, location, price, status) VALUES (?, ?, ?, ?)", values)
        conexion.commit()
        data = {
            'cp_id': cp_id
        }
        queue.put(('register_cp', data))
        return {
            'result': 'registered',
            'cp_id': cp_id,
            'price': price
        }
    except sqlite3.IntegrityError:
        return {
            'result': 'denied'
        }
    finally:
        conexion.close()
    

def authorize(cp_id: str) -> dict[str, Any]:
    conexion = sqlite3.connect("/data/Charging_point.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM CP WHERE id = ?", (cp_id,))
    cp_registers = cursor.fetchall()
    conexion.close()
    if len(cp_registers) == 1:
        return {
            'result': 'authorized',
            'cp_id': cp_id,
            'price': cp_registers[0][2]
        }
    else:
        return {
            'result': 'denied',
        }