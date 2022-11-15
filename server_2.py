import threading
import socket
import time
import sys

from ntp_2 import *

if(len(sys.argv) not in (1,3)):
    print("Faltan o hay más argumentos de los aceptados\nPara Ejecutar escriba uno de los siguientes comandos:\npython3 {0} <IP> <PUERTO>\npython3 {0}\npython {0} <IP> <PUERTO>\npython {0}\n".format(sys.argv[0]))
    sys.exit(2)

finalizar_g = False
box = list()
if(len(sys.argv) == 3):
    localIP     = sys.argv[1]
    localPort   = int(sys.argv[2])
else:
    localIP     = "172.25.72.20"
    localPort   = 123

def recepcion_th(sock, caja):
    global finalizar_g
    print("Thread de recepcion inicializado\n")
    while(not finalizar_g):
        try:
            data, address = sock.recvfrom(1024)
            hora_recepcion = time.time()
            print(">> Recibido desde > {}".format(address))
            caja.append((data, address, hora_recepcion))
        except socket.timeout:
            continue
    print("Terminando thread de recepcion")

def envio_th(sock, caja):
    global finalizar_g
    print("Thread de envios inicializado\n")
    while(not finalizar_g):
        if(len(caja) > 0):
            data, address, recvTime = caja.pop(0)
            recvNTP = paqueteNTP()
            recvNTP.decodificar(data)

            if(recvNTP.mode == 3):
                sendNTP = paqueteNTP(mode=4)
            else:
                sendNTP = paqueteNTP(mode=2)
            
            timestamp_int,timestamp_frac = (recvNTP.tx_int, recvNTP.tx_frac)
            sendNTP.stratum = 2
            sendNTP.poll = recvNTP.poll 
            
            sendNTP.orig_int = timestamp_int
            sendNTP.orig_frac = timestamp_frac       
            
            sys_NTP = sysToNTP(recvTime)
            sys_int = toInt(sys_NTP)
            sys_frac = toFrac(sys_NTP)

            #sendNTP.tx_timestamp = sendNTP.ref_timestamp = sendNTP.recv_timestamp = sys_NTP
            sendNTP.tx_int = sendNTP.ref_int = sendNTP.recv_int = sys_int
            sendNTP.tx_frac = sendNTP.ref_frac = sendNTP.recv_frac = sys_frac

            print(">> Enviado a > {}".format(address))
            sock.sendto(sendNTP.codificar(), address)
        else:
            continue
    print("Terminando thread de envios")

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.settimeout(5)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("Servidor UDP levantado y escuchando.\nIP: {0}\nPuerto: {1}".format(localIP,localPort))

recepcion = threading.Thread(target=recepcion_th, args=(UDPServerSocket, box,))
recepcion.start()
envio = threading.Thread(target=envio_th, args=(UDPServerSocket, box,))
envio.start()

while(True):
    try:
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("Cerrando threads")

        finalizar_g = True
        recepcion.join()
        envio.join()

        UDPServerSocket.close()
        print("Adios :(")
        break

