import sqlite3



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

    def __eq__(self, other):
        if isinstance(other, CChargingPoint):
            return self.id == other.id and self.location == other.location and self.price == self.price and self.status == other.status
        return False

    #def caluclate_amount(self, kw):
    #    self.status.set_supplying()
    #    self.consuption_kw = kw
    #    self.cost = self.consumption_kw * self.price

    #    conexion = sqlite3.connect("/data/Charging_point.db")
    #    cursor = conexion.cursor()
    #    cursor.execute(f"UPDATE Charging_Point SET status=\"Supplying\", consumption={kw} WHERE id={self.id}")
    #    conexion.commit()
    #    conexion.close()

    def turn_ON(self):
        #Algo implementado por sergio cabezon
        #generar un productor que vaya diciendo cosiras
        #threading.Thread(target=directives_producer_thread, args=(0,0,0,0), daemon=True).start() 
        #hay que ver como vuelve a su estado normal si ya se hace solo con los sockets o imlpementar algo 
        pass

    
    def turn_OFF(self, conn):
        self.status.set_stopped()
        self.cost = 0
        self.consumption_kw = 0
        self.id_driver = None

        #generar un productor que vaya diciendo cosiras
        #threading.Thread(target=directives_producer_thread, args=(0,0,0,0), daemon=True).start()   


        cursor = conn.cursor()
        cursor.execute("UPDATE CP SET status=? WHERE id=?", (self.status.get_status(), self.id))
        conn.commit()

        

