from threading import Thread
from GUI import *
from central_config import CentralConfig
from monitor_server import MonitorServer
from CChargingPoint import CChargingPoint
from monitor_handler import monitor_handler
import queue
from stx_etx_connection import *


#################################################################################
# NO HE TENIDO EN CUENTA LOS ERRORES QUE LES DEN POR CULO UN RATO YA LO VEREMOS #
#################################################################################
gui_queue = queue.Queue()

#def monitor_server_run(config: CentralConfig, cp_list: list[CChargingPoint]):
#    monitor_server = MonitorServer(config.ip, config.port)
#    monitor_server.listen()
    
#    while True:
#        monitor_server.accept(monitor_handler) # faltaria pasar la data, que es una instancia de
        # un CChargingPoint para que pueda actualizar el estado del cp


def enqueue_message(message_type, data):
    #Método único para enviar mensajes a la GUI
    gui_queue.put((message_type, data))

def process_queue(app):
    conexion = sqlite3.connect("Charging_point.db")
    cursor = conexion.cursor()
    while not gui_queue.empty():
        message_type, data = gui_queue.get()
        if message_type == "helth_status":
            #meter condicion, segun el estado que envie un mensaje o otro
            cursor.execute(f"UPDATE Charging_Point SET status=\"{0}\", consumption={0}")#consumption son los kwh q lleva
            conexion.commit()
            app.update_panel()
            app.add_app_message(f"Update CP {data}")
            
        elif message_type == "register_cp":
            #con los mensajes de kafka deber ser posible construir el cp
            cp = CChargingPoint(0,0,0)
            app.register_cp(cp)

        elif message_type == "supply_request":
            cursor.execute(f"UPDATE Charging_Point SET status=\"{0}\"")#consumption son los kwh q lleva
            conexion.commit() 
            app.update_panel()
            #Ver los mensajes del consumer
            app.add_request_message(f"DATE  STARTTIME  USER    CP")
            
    conexion.close()
    app.root.after(100, process_queue, app)

def directives_producer_thread(producer, target: str, action: str, supply_id: int | None):
    producer._send_directive(target, action, supply_id)

def supply_error_producer_thread(producer, supply_id):
    producer.send_error(supply_id)

def supply_res_producer_thread(producer, drive_id: str, status: bool, reason: str | None, supply_id: int | None):
    producer.send_response(drive_id, status, reason, supply_id)


def health_monitor_thread():
    #no se que puertos brody
    connection = STXETXConnection(0,0)
    running = True
    while running:
        enqueue_message("helth_status", connection.recv_message())
        #Ver como se comprueba que sigue la conexion y cuando pare salir del while

##################################################################################
#!!!!!!!!!!!!!!!!!!!!!!!!!!!toca definir uno para los registros¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡#
##################################################################################

def supply_req_consumer_thread(consumer):
    conexion = sqlite3.connect("Charging_point.db")
    cursor = conexion.cursor()
    #Thread que escucha un topic de Kafka de forma indefinida
    for msg in consumer:
        # Envia mensaje a la GUI
        enqueue_message(("supply_request", msg.value))
    


#VA A HABER UN PROBLEMA CON LA SINCRONIZACION DE LA BD TENGO QUE VERLO MEJOR PERO DE MOMENTO SE QUEDA ASI    
def supply_info_consumer_thread(consumer):
    conexion = sqlite3.connect("Charging_point.db")
    cursor = conexion.cursor()
    #Thread que escucha un topic de Kafka de forma indefinida
    for msg in consumer:
        #No hace falta enviar mensaje a la GUI porque solo modifica la bd
        #como no sé que valores pasa lo dejo comentado :)
        #es tarde ya :(
        #genera un producer para enviar datos al driver, no he visto como se hace confio en ti
        threading.Thread(target=supply_res_producer_thread, args=(0,0,0,0,0), daemon=True).start()
        cursor.execute(f"UPDATE Charging_Point SET status=\"{0}\", consumption={0}")#consumption son los kwh q lleva
        conexion.commit()

    conexion.close()




def main():
    conexion = sqlite3.connect("Charging_point.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM Charging_Point")
    CPs = []
    for cp in cursor.fetchall():
        CPs.append(CChargingPoint(cp[0], cp[1], cp[2]))
    conexion.commit()
    conexion.close()
    
    root = tk.Tk()
    app = CentralApp(root, CPs)

        # Revisar la cola periódicamente
    root.after(100, process_queue, app)
    req_consumer = 0 #crear consumer
    info_consumer = 0 #crear consumer
    threading.Thread(target=health_monitor_thread, daemon=True).start()
    threading.Thread(target=supply_req_consumer_thread, args=(req_consumer), daemon=True).start()
    threading.Thread(target=supply_info_consumer_thread, args=(req_consumer), daemon=True).start()

    try:
        root.mainloop()
    except Exception as e:
        raise Exception("putada gorda", e)
    finally:

        #No se como funciona lo de cerrar pero intuyo que iría aqui
        conexion = sqlite3.connect("Charging_point.db")
        cursor = conexion.cursor()
        cursor.execute("UPDATE Charging_Point SET status=\"Disconnected\", consumption=0")
        conexion.commit()
        conexion.close()
    root = tk.Tk()
    app = CentralApp(root)
    


if __name__ == '__main__':
    main()
