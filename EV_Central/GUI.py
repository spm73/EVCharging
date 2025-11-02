import tkinter as tk
from tkinter import ttk
import random
import time
import threading
from CChargingPoint import *
import sqlite3
from collections import OrderedDict

# Estados y colores
STATES = {
    1: "#4CAF50", # verde, active
    2: "#4CAF50", # verde, supplying
    3: "#F56929", # naranja, stopped
    4: "#4CAF50", # verde, waiting_for_supply
    5: "#FF4C4C", # rojo, broken_down
    6: "#7A7070"  # gris, disconnected
}

class CentralApp:   
    MAX_MESSAGES = 5
    def __init__(self, root, CPs_db, conn, directives_producer):
        self.root = root
        self.root.title("EVCharging Central - Monitorization panel")
        self.root.geometry("950x600")
        self.root.config(bg="#383F8F")

        self.conn = conn

        self.directives_producer = directives_producer


        title = tk.Label(
            root,
            text="CENTRAL - Monitorization panel",
            font=("Helvetica", 18, "bold"),
            bg="#20244E",
            fg="white",
            pady=10
        )
        title.pack()

        # Frame principal
        self.panel = tk.Frame(root, bg="#20244E")
        self.panel.pack(fill="both", expand=True, padx=10, pady=10)

        # Lista de puntos simulados
        self.points = CPs_db

        # Cuadros visuales
        self.cards = []
        self.create_panel()

        self.messages_frame = tk.Frame(root, bg="#383F8F")
        self.messages_frame.pack(fill="x", padx=10, pady=10)

        # Subpaneles de mensajes
        self.requests_frame = tk.Frame(self.messages_frame, bg="#383F8F")
        self.requests_frame.pack(side="left", fill="both", expand=True, padx=(0,5))
        self.app_frame = tk.Frame(self.messages_frame, bg="#383F8F")
        self.app_frame.pack(side="right", fill="both", expand=True, padx=(5,0))

        # Títulos y subtítulos
        self.requests_title = tk.Label(self.requests_frame, text="*** ON_GOING DRIVERS REQUESTS ***", 
                                    font=("Helvetica", 12, "bold"), bg="#383F8F", fg="white")
        self.requests_title.pack(anchor="w")

        self.requests_subtitle = tk.Label(self.requests_frame, text="DATE | START TIME | User ID | CP",
                                        font=("Helvetica", 10, "bold"), bg="#383F8F", fg="white")
        self.requests_subtitle.pack(anchor="w")

        self.app_title = tk.Label(self.app_frame, text="*** APPLICATION MESSAGES ***", 
                                font=("Helvetica", 12, "bold"), bg="#383F8F", fg="white")
        self.app_title.pack(anchor="w")

        # Contenedores de mensajes
        self.requests_msgs = OrderedDict()
        self.app_msgs = []


    def create_panel(self):
        """Crea los cuadros para cada punto"""
        for i, cp in enumerate(self.points):
            frame = tk.Frame(self.panel, bg=STATES[6], relief="raised", bd=2)
            frame.grid(row=i // 4, column=i % 4, padx=10, pady=10, ipadx=10, ipady=10, sticky="nsew")

            lbl_id = tk.Label(frame, text= f"Cp={cp.id}" , font=("Arial", 16, "bold"), bg=STATES[6], fg="white")
            lbl_id.pack(anchor="w")

            lbl_location = tk.Label(frame, font=("Arial", 10, "bold"),text=f"Location: {cp.location}", bg=STATES[6], fg="white")
            lbl_location.pack(anchor="w")

            lbl_price = tk.Label(frame, font=("Arial", 10, "bold"),text=f"Price: {cp.price} €/kWh", bg=STATES[6], fg="white")
            lbl_price.pack(anchor="w")

            lbl_info = tk.Label(frame, font=("Arial", 10, "bold"),text="", bg=STATES[6], fg="white")
            lbl_info.pack()
            button = ttk.Button(frame, text="Power_OFF", command=lambda cp=cp: self.status_swap(cp.id))
            button.pack(pady=(0, 10))

            self.cards.append({
                "frame": frame,
                "lbl_info": lbl_info,
                "lbl_id": lbl_id,
                "lbl_location":lbl_location,
                "lbl_price": lbl_price,
                "cp": cp,
                "button": button
            })

        for i in range(4):
            self.panel.grid_columnconfigure(i, weight=1)

    def update_panel(self):
        #Actualiza los cuadros con los datos actuales
        for card in self.cards:
            cp = card["cp"]
            frame = card["frame"]
            lbl_info = card["lbl_info"]
            lbl_id = card["lbl_id"]
            lbl_location = card["lbl_location"]
            lbl_price = card["lbl_price"]

            frame_color = STATES[cp.status.get_status()]
            frame.config(bg=frame_color)
            lbl_id.config(bg=frame_color)
            lbl_location.config(bg=frame_color)
            lbl_price.config(bg=frame_color)

            if cp.status == "Supplying":
                info = f"Consumption: {cp.consumption_kw} kW\nCost: {cp.cost} €\nDriver: {cp.id_driver}"
            elif cp.status == "Stopped":
                info = "Out of order"
            else:
                info = ""

            lbl_info.config(text=info, bg=frame_color)

        # Si al menos un punto sigue en 'Supplying', vuelve a llamar a update_panel después de X ms
        #if any(card["cp"].status == "Supplying" for card in self.cards):
        #    self.panel.after(1000, self.update_panel)


    def status_swap(self, cp_id):
        card = [card for card in self.cards if card["cp"].id == cp_id][0]
        cp = card["cp"]
        button = card["button"]
        if button["text"] == "Power_ON":
            try:
                self.directives_producer.resume_cp(cp.id_driver)
            except Exception as e:
                raise e
            try:
                cp.turn_ON()
            except Exception as e:
                raise Exception("There was a problem turning ON", e)
            button.config(text = "Power_OFF")
        elif button["text"] == "Power_OFF":
            try:
                self.directives_producer.stop_cp(cp.id_driver)
            except Exception as e:
                raise e
            try:
                cp.turn_OFF(self.conn)
            except Exception as e:
                raise Exception("There was a problem turning OFF", e)
            self.add_app_message(f"Cp {cp.id} out of order", color="#FF4C4C")
            button.config(text = "Power_ON")
        else:
            raise Exception("There was a problem with the button")
        
        self.update_panel()



    def add_request_message(self, msg, cp_id):
        #Añade un mensaje de driver request, los más recientes arriba
        label = tk.Label(self.requests_frame, text=msg, bg="#383F8F", fg="white", anchor="w")

        if self.requests_msgs:
            first_msg = next(iter(self.requests_msgs.values()))
            label.pack(anchor="w", before=first_msg)
        else:
            label.pack(anchor="w", after=self.requests_subtitle)

        self.requests_msgs[cp_id] = label


    def delete_request_message(self, cp_id):
        if cp_id in self.requests_msgs:
            old_label = self.requests_msgs[cp_id]
            del self.requests_msgs[cp_id]
            old_label.destroy()
        else:
            # Opcional: loggear que no se encontró el mensaje
            print(f"Warning: No se encontró mensaje para CP {cp_id}")


    def add_app_message(self, msg, color="white"):
        #Añade un mensaje de aplicación, los más recientes arriba
        label = tk.Label(self.app_frame, text=msg, bg="#383F8F", fg=color, anchor="w")

        if self.app_msgs:
            label.pack(anchor="w", before=self.app_msgs[0])
        else:
            label.pack(anchor="w", after=self.app_title)

        self.app_msgs.insert(0, label)

        if len(self.app_msgs) > self.MAX_MESSAGES:
            old_label = self.app_msgs.pop()  # eliminar el más antiguo
            old_label.destroy()


    def update_fromDB(cp_id):
        cursor = conexion.cursor()
        cursor.execute(f"SELECT * FROM CP WHERE id={cp_id}")
        cp_db = cursor.fetchall()[0]
        cp = CChargingPoint(cp[0],cp[1],cp[2])
        cp.status.set_active()
        return cp



    def register_cp(self, cp_id):
        
        cp = self.update_fromDB(cp_id)

        self.points.append(cp)
        frame = tk.Frame(self.panel, bg=STATES[6], relief="raised", bd=2)
        frame.grid(row=len(self.cards) // 4, column=len(self.cards) % 4, padx=10, pady=10, ipadx=10, ipady=10, sticky="nsew")

        lbl_id = tk.Label(frame, text= f"Cp={cp.id}" , font=("Arial", 16, "bold"), bg=STATES[6], fg="white")
        lbl_id.pack(anchor="w")

        lbl_location = tk.Label(frame, font=("Arial", 10, "bold"),text=f"Location: {cp.location}", bg=STATES[6], fg="white")
        lbl_location.pack(anchor="w")

        lbl_price = tk.Label(frame, font=("Arial", 10, "bold"),text=f"Price: {cp.price} €/kWh", bg=STATES[6], fg="white")
        lbl_price.pack(anchor="w")

        lbl_info = tk.Label(frame, font=("Arial", 10, "bold"),text="", bg=STATES[6], fg="white")
        lbl_info.pack()
        button = ttk.Button(frame, text="Power_OFF", command=lambda cp=cp: self.status_swap(cp.id))
        button.pack(pady=(0, 10))

        self.cards.append({
            "frame": frame,
            "lbl_info": lbl_info,
            "lbl_id": lbl_id,
            "lbl_location":lbl_location,
            "lbl_price": lbl_price,
            "cp": cp,
            "button": button
        })


        self.update_panel()

    def modify_cp_status(self, cp_id, action):
        modified = False
        for cp in self.points:
            if cp.id != cp_id: 
                continue
            
            match action:
                case 'set_active':
                    cp.status.set_active()
                case 'set_supplying':
                    cp.status.set_supplying()
                case 'set_stopped':
                    cp.status.set_stopped()
                case 'set_waiting_for_supplying':
                    cp.status.set_waiting_for_supplying()
                case 'set_broken_down':
                    cp.status.set_broken_down()
                case 'set_disconnected':
                    cp.status.set_disconnected()
                case _:
                    cp.status.set_disconnected()
                    
            cursor = self.conn.cursor()
            cursor.execute(f"UPDATE Charging_Point SET status=\"{cp.status.get_status()}\"")
            self.conn.commit()
            modified = True
            break
        
        if modified:
            self.update_panel()
        else:
            raise Exception("this CP wasn't registered")
        
    def check_cp_active(self,cp_id):
        existing = False
        for cp in self.points:
            if cp.id == cp_id: 
                return cp.status.is_active()
                # if cp.is_active():
                #     return True
                # existing = True
        
        # if existing:
        #     return False
        # else:
        #     raise Exception("this CP wasn't registered")
        raise Exception("this CP wasn't registered")
        


    def modify_cp_driverid(self, cp_id, driver_id):
        modified = False
        for cp in self.points:
            if cp.id == cp_id:
                cp.id_driver = driver_id
                modified = True
                break
                
        if modified:
            self.update_panel()
        else:
            raise Exception("this CP wasn't registered")

        
    def modify_cp_info(self, cp_id, consumption, cost):
        modified = False
        for cp in self.points:
            if cp.id == cp_id:
                cp.consumption_kw = consumption
                cp.cost = cost
                modified = True
                break
                
        if modified:
            self.update_panel()
        else:
            raise Exception("this CP wasn't registered")

    def reset_cp(self, cp_id):
        modified = False
        for cp in self.points:
            if cp.id == cp_id:
                cp.consumption_kw = 0
                cp.cost = 0
                cp.id_driver = None
                modified = True
                break
                
        if modified:
            self.update_panel()  # Añadir para actualizar la UI
        else:
            raise Exception(f"CP {cp_id} wasn't registered")
            


if __name__ == "__main__":
    root = tk.Tk()
    conexion = sqlite3.connect("/data/Charging_point.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM Charging_Point")
    CPs = []
    for cp in cursor.fetchall():
        CPs.append(CChargingPoint(cp[0], cp[1], cp[2]))
    conexion.commit()
    conexion.close()
    
    app = CentralApp(root, CPs)
    try:
        root.mainloop()
    except Exception as e:
        raise Exception("putada gorda", e)
    finally:
        conexion = sqlite3.connect("/data/Charging_point.db")
        cursor = conexion.cursor()
        cursor.execute("UPDATE Charging_Point SET status=\"Disconnected\", consumption=0")
        conexion.commit()
        conexion.close()