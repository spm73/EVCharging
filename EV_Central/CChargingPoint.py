import sqlite3
import threading
from main import *

from cp_status import CPStatus

class CChargingPoint:
    def __init__(self, id_cp, location, price):
        self.id = id_cp
        self.location = location
        self.price = price 
        self.status = CPStatus()
        self.consumption_kw = 0.0
        self.cost = 0.0
        self.id_driver = None

    def caluclate_amount(self, kw):
        self.status.set_supplying()
        self.consuption_kw = kw
        self.cost = self.consumption_kw * self.price

        conexion = sqlite3.connect("Charging_point.db")
        cursor = conexion.cursor()
        cursor.execute(f"UPDATE Charging_Point SET status=\"Supplying\", consumption={kw} WHERE id={self.id}")
        conexion.commit()
        conexion.close()

    def turn_ON(self):
        #Algo implementado por sergio cabezon
        #generar un productor que vaya diciendo cosiras
        threading.Thread(target=directives_producer_thread, args=(0,0,0,0), daemon=True).start() 
        #hay que ver como vuelve a su estado normal si ya se hace solo con los sockets o imlpementar algo 
        try:
            self.update_fromDB()
        except Exception as e:
            raise Exception("Problema con actualizar db", e)
    
    def turn_OFF(self):
        self.status.set_stopped()
        self.cost = 0
        self.consumption_kw = 0
        self.id_driver = None

        #generar un productor que vaya diciendo cosiras
        threading.Thread(target=directives_producer_thread, args=(0,0,0,0), daemon=True).start()   

        conexion = sqlite3.connect("Charging_point.db")
        cursor = conexion.cursor()
        cursor.execute(f"UPDATE Charging_Point SET status=\"Stopped\", consumption=0 WHERE id={self.id}")
        conexion.commit()
        conexion.close()
        

    def update_fromDB(self):
        conexion = sqlite3.connect("Charging_point.db")
        cursor = conexion.cursor()
        cursor.execute(f"SELECT * FROM Charging_Point WHERE id={self.id}")
        cp = cursor.fetchall()[0]
        conexion.commit()
        conexion.close()
        
        self.id = cp[0]
        self.location = cp[1]
        self.price = cp[2]
        self.status = cp[3]
        self.consumption_kw = cp[4]