import os
import queue
from threading import Thread, Event
from .events import *
from decimal import Decimal


class TerminalHandler:
    # Ahora recibe la cola central desde fuera
    def __init__(self, cola_central: queue.Queue):
        self.__cola_central = cola_central 
        self.__is_listening = Event()
        self.__thread = Thread(target=self.__listening_loop, daemon=True)
        self.__thread.start()

    def start_listening(self) -> None:
        self.__is_listening.set()

    def stop_listening(self) -> None:
        self.__is_listening.clear()

    def __listening_loop(self):
        self.__is_listening.wait()
        
        while self.__is_listening.is_set():
            try:
                comando = input()
                if self.__is_listening.is_set():
                    # Empaquetamos el input en el formato estándar y lo enviamos
                    evento = SystemEvent(intention=Intention.KEYBOARD_INPUT, data=comando)
                    self.__cola_central.put(evento)
            except EOFError:
                break
    
# --- MÉTODOS ESTÁTICOS ---

    @staticmethod
    def clean():
        """Limpia la consola independientemente del sistema operativo."""
        # 'nt' es Windows, el resto (Linux/Mac) usan 'clear'
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def printSupplyingInfo(price: Decimal, consumption: int):
        TerminalHandler.clean()
        print("Supplying Data:")
        print(f"Current consumption: {consumption} kWh | Current cost: {price}€")

    @staticmethod
    def printSupplyingTicket(price: Decimal, consumption: int):
        TerminalHandler.clean()
        print(f"================================\n\t\t\tCHARGING SUMMARY\n================================\n\tEnergy Consumed : {consumption} kWh\n\tTotal Price     : {price}€\n================================\nThank you for using our CP!")

    @staticmethod
    def printCP(cp_list: list) -> None:
        TerminalHandler.clean()
        if not cp_list: 
            print("loading Charging Points from central...\nThis may take a few seconds")
            return
        
        print("Available Charging Points")
        for indice, elemento in enumerate(cp_list, start=1):
            print(f">>>>> [{indice}] {elemento}")

        print("<<<< select one Charging point >>>>")