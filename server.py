import threading
import socket
import time
import sys

from ntp import *

if(len(sys.argv) not in (1,3,5)):
    print('''Faltan o hay más argumentos de los aceptados
Para Ejecutar utilice uno de los siguientes comandos:
<Ejecutable de Python> {0} <IP> <PUERTO> <Numero de threads de recepcion> <Numero de threads de trabajo>
<Ejecutable de Python> {0} <IP> <PUERTO>
<Ejecutable de Python> {0}'''.format(sys.argv[0]))
    sys.exit(2)

finalizar_g = False
box = list()
if(len(sys.argv) >= 3 and len(sys.argv) <= 5):
    localIP     = sys.argv[1]
    localPort   = int(sys.argv[2])
    if(len(sys.argv) == 5):
        if(int(sys.argv[3]) > 1):
            threads_recepcion = int(sys.argv[3])
        else:
            threads_recepcion = 1
        if(int(sys.argv[4]) > 1):
            threads_trabajo = int(sys.argv[4])
        else:
            threads_trabajo = 1
    else:
        threads_recepcion = 1
        threads_trabajo = 1
else:
    localIP     = "localhost"
    localPort   = 123
    threads_recepcion = 1
    threads_trabajo = 1

def recepcion_th(sock, lock, caja, id):
    global finalizar_g
    print("Thread de recepcion {} inicializado\n".format(id))
    while(not finalizar_g):
        try:
            data, address = sock.recvfrom(1024)
            hora_recepcion = time.time()
            print(">> RecID {0} - Recibido desde {1}".format(id,address))
            with lock:
                caja.append((data, address, hora_recepcion))
        except socket.timeout:
            continue
    print("Terminando thread de recepcion {}".format(id))

def trabajo_th(sock, lock, caja, id):
    global finalizar_g
    print("Thread de trabajo {} inicializado\n".format(id))
    while(not finalizar_g):
        if(len(caja) > 0):
            with lock:
                data, address, recvTime = caja.pop(0)
            try:
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

                sendNTP.tx_int = sendNTP.ref_int = sendNTP.recv_int = sys_int
                sendNTP.tx_frac = sendNTP.ref_frac = sendNTP.recv_frac = sys_frac

                print(">> TrabajoID {0} - Enviado a {1}".format(id,address))
                sock.sendto(sendNTP.codificar(), address)
            except NTPException:
                print(">> TrabajoID {0} - Contenido del mensaje no es del formato NTP.".format(id))
                continue
        else:
            continue
    print("Terminando thread de envios {}".format(id))

#Creacion del socket UDP + establecimiento de temporizador
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.settimeout(5)

#Establecimiento del socket en el puerto y direccion correspondientes
UDPServerSocket.bind((localIP, localPort))
print("Servidor UDP levantado y escuchando.\nIP: {0}\nPuerto: {1}".format(localIP,localPort))

cerradura_recepcion = threading.Lock()
cerradura_trabajo = threading.Lock()

all_threads = list()

for x in range(threads_recepcion):      
    recepcion = threading.Thread(target=recepcion_th, args=(UDPServerSocket, cerradura_recepcion, box, x,))
    recepcion.start()
    all_threads.append(recepcion)

for x in range(threads_trabajo):
    trabajo = threading.Thread(target=trabajo_th, args=(UDPServerSocket, cerradura_trabajo, box, x,))
    trabajo.start()
    all_threads.append(trabajo)

while(True):
    try:
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("Cerrando threads")

        finalizar_g = True
        for t in all_threads:
            t.join()

        UDPServerSocket.close()
        print("Adios :(")
        break

