import socket
import inspect
import sys
from ntp_2 import *
import time

if(len(sys.argv) not in (1,3)):
    print("Faltan o hay más argumentos de los aceptados\nPara Ejecutar escriba uno de los siguientes comandos:\npython3 {0} <IP> <PUERTO>\npython3 {0}\npython {0} <IP> <PUERTO>\npython {0}\n".format(sys.argv[0]))
    sys.exit(2)

def inspeccion(clase):
    #Inspeccion de clase
    attributes = inspect.getmembers(clase, lambda a:not(inspect.isroutine(a)))
    msg = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
    print(*msg, sep="\n")

if(len(sys.argv) == 3):
    serverAddressPort = (sys.argv[1], int(sys.argv[2]))
else:
    serverAddressPort = ("172.25.72.20", 123)

bufferSize = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket

while(True):
    sendNTP = paqueteNTP()
    #inspeccion(sendNTP) #Inspeccion de los contenidos de la clase / paquete enviado
    UDPClientSocket.sendto(sendNTP.codificar(), serverAddressPort)

    msgFromServer = UDPClientSocket.recvfrom(bufferSize)

    recvNTP = paqueteNTP()
    recvNTP.decodificar(msgFromServer[0])
    #inspeccion(recvNTP) #Inspeccion de los contenidos de la clase / paquete recibido
    timeNTP = toTime(recvNTP.tx_int,recvNTP.tx_frac) - NTP_DELTA

    print(time.ctime(timeNTP).replace("  ", " "))
    time.sleep(2.5)
