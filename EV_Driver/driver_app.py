import time

if __name__ == "__main__":
    CPs = []
    with open("cp_list.txt", "r") as archivo:
        for linea in archivo:
            CPs.append(linea.strip())

    next_cp = 0

    while True:
        print(f"> These are the existing charging points: ")
        for i in range(len(CPs) - 1):
            print(CPs[i], end= ", " )
        print(CPs[len(CPs) - 1])
        print("_____________________Instructions____________________")
        print(" - If you want to connect to a specific one, write its name.")
        print(" - If you want to connect to the next one in the list, type anything")
        print(" - If you expect to close the application, type \"quit\"")
        cp = input("---> ")
        if cp in CPs:
            print(f"Connecting with CP {cp}...")
            #enviar una peticion a central a cp
            next_cp = (CPs.index(cp) + 1) % len(CPs)
        elif cp == "quit":
            break
        else:
            print(f"Connecting with CP {CPs[next_cp]}...")
            #enviar una peticion a central a CPs[next_cp]
            next_cp = (next_cp + 1) % len(CPs)
        time.sleep(4)
            
            

