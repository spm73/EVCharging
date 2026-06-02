import queue
import time

from events import *

EVENT_QUEUE = queue.Queue()

def wait_for_events(*intenciones_deseadas: Intention) -> SystemEvent:
    """
    Busca en la cola hasta encontrar un evento que coincida con las intenciones dadas.
    Si saca un evento que no coincide, lo devuelve al final y hace una pequeña pausa.
    """
    while True:
        # get() bloquea de forma natural al 0% de CPU si la cola está totalmente vacía
        event = EVENT_QUEUE.get()
        
        if event.intention in intenciones_deseadas:
            # ¡Lo encontramos! Lo devolvemos al lugar donde llamaron a la función
            return event
            
        else:
            # No es de los que buscamos. Lo mandamos al final de la cola.
            EVENT_QUEUE.put(event)
            
            # Tu sleep de un cuarto de segundo para evitar el efecto "lavadora"
            # y no saturar la CPU leyendo sin parar los mismos mensajes devueltos.
            time.sleep(0.25)