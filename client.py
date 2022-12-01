import socket
import sys
from ntp import *
import time

if(len(sys.argv) not in (1,3)):
    print('''Faltan o hay más argumentos de los aceptados
Para Ejecutar utilice uno de los siguientes comandos:
<Ejecutable de Python> {0} <IP> <PUERTO>
<Ejecutable de Python> {0}'''.format(sys.argv[0]))
    sys.exit(2)

if(len(sys.argv) == 3):
    serverAddressPort = (sys.argv[1], int(sys.argv[2]))
else:
    serverAddressPort = ("localhost", 123)

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
sendNTP = paqueteNTP()
UDPClientSocket.sendto(sendNTP.codificar(), serverAddressPort)

msgFromServer = UDPClientSocket.recvfrom(1024)
recvNTP = paqueteNTP()
recvNTP.decodificar(msgFromServer[0])
timeNTP = toTime(recvNTP.tx_int,recvNTP.tx_frac) - NTP_DELTA

print(time.ctime(timeNTP).replace("  ", " "))