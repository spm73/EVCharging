import sys
import select
import time
def try_connexion():
    print("Connecting with the CENTRAL...")
    try:
        #cosas
        pass
    except:
        raise Exception("No se ha logrado la conexion")
    print("Conexion con exito")


def engine_app(driver_ip):
    print(f"____________________Driver {driver_ip} connected___________________")
    print(" - Do you want to plug the car?(n/y | default y)")
    response = input("---> ")
    if response=="n":
        return
    #esto lo tiene que cambiar de una clase
    status="Supplying"
    #enviar a central
    time_ini = time.time()
    print("Presione \'Enter\' para desconectar:")
    while status=="Supplying":
        time_fin = time.time()

        #enviar los datos donde sea
        print(f"\r{' ' * 50}\rTiempo = {time_fin - time_ini:.2f}s", end="")
        sys.stdout.flush()

        if select.select([sys.stdin], [], [], 0)[0]:
            input()  # limpia el buffer
            status="Active"

    #enviar ticket
    print("\"\"\"Muchas gracias por usar uno de nuestros puntos :)\"\"\"")

    
if __name__=="__main__":
    try_connexion()
    #toca hacer algo que espere alguna conexion de driver
    driver_ip = 0
    engine_app(driver_ip)
