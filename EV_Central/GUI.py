import tkinter as tk
from tkinter import ttk
import random
import time
import threading
from CChargingPoint import *
import sqlite3

# Estados y colores
STATES = {
    "Activated": "#4CAF50",        # verde
    "Stopped": "#F56929",          # naranja
    "Supplying": "#4CAF50",   # verde
    "Broken": "#FF4C4C",        # rojo
    "Disconnected": "#7A7070"     # gris
}

class CentralApp:   
    MAX_MESSAGES = 5
    def __init__(self, root, CPs_db):
        self.root = root
        self.root.title("EVCharging Central - Monitorization panel")
        self.root.geometry("950x600")
        self.root.config(bg="#383F8F")

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
        self.puntos = CPs_db

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
        self.requests_msgs = []
        self.app_msgs = []



    def create_panel(self):
        """Crea los cuadros para cada punto"""
        for i, cp in enumerate(self.puntos):
            frame = tk.Frame(self.panel, bg=STATES["Disconnected"], relief="raised", bd=2)
            frame.grid(row=i // 3, column=i % 3, padx=10, pady=10, ipadx=10, ipady=10, sticky="nsew")

            lbl_id = tk.Label(frame, text= f"Cp={cp.id}" , font=("Arial", 16, "bold"), bg=STATES["Disconnected"], fg="white")
            lbl_id.pack(anchor="w")

            lbl_location = tk.Label(frame, font=("Arial", 10, "bold"),text=f"Location: {cp.location}", bg=STATES["Disconnected"], fg="white")
            lbl_location.pack(anchor="w")

            lbl_price = tk.Label(frame, font=("Arial", 10, "bold"),text=f"Price: {cp.price} €/kWh", bg=STATES["Disconnected"], fg="white")
            lbl_price.pack(anchor="w")

            lbl_info = tk.Label(frame, font=("Arial", 10, "bold"),text="", bg=STATES["Disconnected"], fg="white")
            lbl_info.pack()
            button = ttk.Button(frame, text="Power_ON", command=lambda cp=cp: self.status_swap(cp.id))
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

        for i in range(3):
            self.panel.grid_columnconfigure(i, weight=1)

    def update_panel(self):
        """Actualiza los cuadros con los datos actuales"""
        for card in self.cards:
            cp = card["cp"]
            cp.update_fromDB()
            frame = card["frame"]
            lbl_info = card["lbl_info"]
            lbl_id = card["lbl_id"]
            lbl_location = card["lbl_location"]
            lbl_price = card["lbl_price"]

            frame.config(bg=STATES[cp.status])
            lbl_id.config(bg=STATES[cp.status])
            lbl_location.config(bg=STATES[cp.status])
            lbl_price.config(bg=STATES[cp.status])

            if cp.status == "Supplying":
                info = f"Consumption: {cp.consumption_kw} kW\nCost: {cp.cost} €\nDriver: {cp.id_driver}"
            elif cp.status == "Stopped":
                info = "Out of order"
            else:
                info = ""

            lbl_info.config(text=info, bg=STATES[cp.status])

        # Si al menos un punto sigue en 'Supplying', vuelve a llamar a update_panel después de X ms
        if any(card["cp"].status == "Supplying" for card in self.cards):
            self.panel.after(1000, self.update_panel)


    def status_swap(self, cp_id):
        card = [card for card in self.cards if card["cp"].id == cp_id][0]
        cp = card["cp"]
        button = card["button"]
        if button["text"] == "Power_ON":
            try:
                cp.turn_ON()
            except Exception as e:
                raise Exception("There was a problem turning ON", e)
            button.config(text = "Power_OFF")
        elif button["text"] == "Power_OFF":
            try:
                cp.turn_OFF()
            except Exception as e:
                raise Exception("There was a problem turning OFF", e)
            self.add_app_message(f"Cp {cp.id} out of order", color="#FF4C4C")
            button.config(text = "Power_ON")
        else:
            raise Exception("There was a problem with the buttom")
        
        self.update_panel()


    def add_request_message(self, msg):
        """Añade un mensaje de driver request, los más recientes arriba"""
        label = tk.Label(self.requests_frame, text=msg, bg="#383F8F", fg="white", anchor="w")

        if self.requests_msgs:
            label.pack(anchor="w", before=self.requests_msgs[0])
        else:
            label.pack(anchor="w", after=self.requests_subtitle)

        self.requests_msgs.insert(0, label)

        if len(self.requests_msgs) > self.MAX_MESSAGES:
            old_label = self.requests_msgs.pop()  # eliminar el más antiguo
            old_label.destroy()


    def add_app_message(self, msg, color="white"):
        """Añade un mensaje de aplicación, los más recientes arriba"""
        label = tk.Label(self.app_frame, text=msg, bg="#383F8F", fg=color, anchor="w")

        if self.app_msgs:
            label.pack(anchor="w", before=self.app_msgs[0])
        else:
            label.pack(anchor="w", after=self.app_title)

        self.app_msgs.insert(0, label)

        if len(self.app_msgs) > self.MAX_MESSAGES:
            old_label = self.app_msgs.pop()  # eliminar el más antiguo
            old_label.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    conexion = sqlite3.connect("Charging_point.db")
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
        conexion = sqlite3.connect("Charging_point.db")
        cursor = conexion.cursor()
        cursor.execute("UPDATE Charging_Point SET status=\"Disconnected\", consumption=0")
        conexion.commit()
        conexion.close()