import threading
from confluent_kafka import KafkaException
from GUI import *
from central_config import CentralConfig
from monitor_server import MonitorServer
from CChargingPoint import CChargingPoint
from monitor_handler import monitor_handler
import queue
from stx_etx_connection import *
from directives_producer import DirectivesProducer
from supply_error_producer import SupplyErrorProducer
from supply_info_consumer import SupplyInfoConsumer
from supply_info_producer import SupplyInfoProducer
from supply_req_consumer import SupplyReqConsumer
from supply_res_producer import SupplyResProducer
from datetime import datetime, date



#################################################################################
# NO HE TENIDO EN CUENTA LOS ERRORES QUE LES DEN POR CULO UN RATO YA LO VEREMOS #
#################################################################################
gui_queue = queue.Queue()

def monitor_server_run(config: CentralConfig):
    monitor_server = MonitorServer(config.ip, config.port)
    monitor_server.listen()
    
    while True:
        monitor_server.accept(monitor_handler, gui_queue)


def enqueue_message(message_type, data):
    #Método único para enviar mensajes a la GUI
    gui_queue.put((message_type, data))

def process_queue(app):
    while not gui_queue.empty():
        message_type, data = gui_queue.get()

        if message_type == "helth_status":
            #meter condicion, segun el estado que envie un mensaje o otro
            app.modify_cp_status(data['cp_id'],data['action'])#cp_id, consumption, cost


        elif message_type == "register_cp":
            #con los mensajes de kafka deber ser posible construir el cp
            app.register_cp(data)

        elif message_type == "supply_request":
            if app.check_cp_active(data['cp_id']):#cp_id, status
                app.modify_cp_driverid(data['cp_id'],data['applicant_id'])#cp_id, driver_id
            #Ver los mensajes del consumer
            app.add_request_message(f"{date.today()}  {datetime.now().time()}  {data['applicant_id']}    {data['cp_id']}", data['cp_id'])#cp_id
        
        elif message_type == "supply_info":
            app.modify_cp_info(0,0,0)#cp_id, consumption, cost

        elif message_type == "supply_ticket":
            #Ver los mensajes del consumer
            app.delete_request_message(data['cp_id'])#cp_id

            
    app.root.after(100, process_queue, app)

def directives_producer_thread(producer, target: str, action: str, supply_id: int | None):
    producer._send_directive(target, action, supply_id)

def supply_error_producer_thread(producer, supply_id):
    producer.send_error(supply_id)

def supply_res_producer_thread(producer, drive_id: str, status: bool, reason: str | None, supply_id: int | None):
    producer.send_response(drive_id, status, reason, supply_id)

##################################################################################
#!!!!!!!!!!!!!!!!!!!!!!!!!!!toca definir uno para los registros¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡¡#
##################################################################################

def supply_req_consumer_thread(consumer: SupplyReqConsumer):
    while running:
        request = None
        while not request:
            try:
                request = consumer.get_request()
            except KafkaException as e:
                error = str(e.args[0])
                print(error) # Si lo puedes hacer más bonito mejor
        enqueue_message("supply_request", request)
    


#VA A HABER UN PROBLEMA CON LA SINCRONIZACION DE LA BD TENGO QUE VERLO MEJOR PERO DE MOMENTO SE QUEDA ASI    
def supply_info_consumer_thread(consumer: SupplyInfoConsumer, producer: SupplyInfoProducer):
    while running:
        info = None
        while not info:
            try:
                info = consumer.get_info()
            except KafkaException as e:
                error = str(e.args[0])
                print(error) # Si lo puedes hacer más bonito mejor
        producer.repeat_msg(info)
        if info.get('type') == 'supplying':
            enqueue_message("supply_info", info)
        elif info.get('type') == 'ticket':
            enqueue_message("supply_ticket", info)


running = True
current_supply_id = 1

def main():
    config = CentralConfig()
    threading.Thread(target=monitor_server_run, args=(config))
    req_consumer = SupplyReqConsumer(config.kafka_ip, config.kafka_port)
    info_consumer = SupplyInfoConsumer(config.kafka_ip, config.kafka_port)
    info_producer = SupplyInfoProducer(config.kafka_ip, config.kafka_port)
    directives_producer = DirectivesProducer(config.kafka_ip, config.kafka_port)
    res_producer = SupplyResProducer(config.kafka_ip, config.kafka_port)
    error_producer = SupplyErrorProducer(config.kafka_ip, config.kafka_port)
    conexion = sqlite3.connect("Charging_point.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM CP")
    CPs = []
    for cp in cursor.fetchall():
        CPs.append(CChargingPoint(cp[0], cp[1], cp[2]))

    
    root = tk.Tk()
    app = CentralApp(root, CPs, conexion, directives_producer)

        # Revisar la cola periódicamente
    root.after(100, process_queue, app)
    threading.Thread(target=supply_req_consumer_thread, args=(req_consumer), daemon=True).start()
    threading.Thread(target=supply_info_consumer_thread, args=(info_consumer, info_producer), daemon=True).start()

    try:
        root.mainloop()
    except Exception as e:
        raise Exception("putada gorda", e)
    finally:
        running = False
        #No se como funciona lo de cerrar pero intuyo que iría aqui
        cursor = conexion.cursor()
        cursor.execute("UPDATE CP SET status=\"Disconnected\"")
        conexion.commit()
        conexion.close()

    


if __name__ == '__main__':
    main()
