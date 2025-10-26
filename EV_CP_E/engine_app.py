import sys
import select
import time

from cp_status import CPStatus
from supply_info import SupplyInfo

def try_connexion():
    print("Connecting with the CENTRAL...")
    try:
        #cosas
        pass
    except:
        raise Exception("The connection wasn't possible")
    print("Successful connection")


def engine_app(price):
    print(f"____________________Driver connected___________________")
    print(" - Do you want to plug the car?(n/y | default y)")
    response = input("---> ")
    if response=="n":
        return
    #esto lo tiene que cambiar de una clase
    status="Supplying"
    #enviar a central
    time_ini = time.time()
    print("Press \'Enter\' to unplug:")
    while status=="Supplying":
        time_plug = time.time() - time_ini
        #Suponemos que son puntos semirápidos(AC) de 22kw
        amount = time_plug*(22/3600)
        cost = amount*price
        #enviar los datos donde sea
        print(f"\r{' ' * 60}\rTime = {time_plug:.2f}s    Amount = {amount:.4f}kwh   Cost = {cost:.4f}€", end="")
        sys.stdout.flush()

        if select.select([sys.stdin], [], [], 0)[0]:
            input()  # limpia el buffer
            print("\n")
            status="Active"

    #enviar ticket
    print("\"\"\" Thank you for using our service. :)\"\"\"")


def supply_interface(cp_status: CPStatus, supply_info: SupplyInfo):
    print(f"____________________Driver connected___________________")
    print(" - Do you want to plug the car?(n/y | default y)")
    response = input("---> ")
    if response == "n":
        return
    #esto lo tiene que cambiar de una clase
    cp_status.set_supplying()
    #enviar a central
    time_ini = time.time()
    print("Press \'Enter\' to unplug:")
    while cp_status.is_supplying():
        time_plug = time.time() - time_ini
        #Suponemos que son puntos semirápidos(AC) de 22kw
        supply_info.send_info()
        amount = supply_info.get_current_consumption()
        cost = supply_info.get_current_price()
        #enviar los datos donde sea
        print(f"\r{' ' * 60}\rTime = {time_plug:.2f}s    Consumption = {amount:.4f}kwh   Cost = {cost:.4f}€", end="")
        sys.stdout.flush()

        if select.select([sys.stdin], [], [], 0)[0]:
            input()  # limpia el buffer
            print("\n")
            cp_status.set_active()

    #enviar ticket
    print("\"\"\" Thank you for using our service. :)\"\"\"")

    
if __name__=="__main__":
    try_connexion()
    #toca hacer algo que espere alguna conexion de driver
    driver_ip = 0
    engine_app(driver_ip, 0.54)
