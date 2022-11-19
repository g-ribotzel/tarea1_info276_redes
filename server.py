import threading
import socket
import time
import sys

from ntp import *

if(len(sys.argv) not in (1,3)):
    print("Faltan o hay más argumentos de los aceptados\nPara Ejecutar escriba uno de los siguientes comandos:\npython3 {0} <IP> <PUERTO>\npython3 {0}\npython {0} <IP> <PUERTO>\npython {0}\n".format(sys.argv[0]))
    sys.exit(2)

finalizar_g = False
box = list()
if(len(sys.argv) == 3):
    localIP     = sys.argv[1]
    localPort   = int(sys.argv[2])
else:
    localIP     = "localhost"
    localPort   = 123

def recepcion_th(sock, lock, caja, id):
    global finalizar_g
    print("Thread de recepcion {} inicializado\n".format(id))
    while(not finalizar_g):
        try:
            data, address = sock.recvfrom(1024)
            hora_recepcion = time.time()
            print(">> RecID {0} Recibido desde {1}".format(id,address))
            with lock:
                caja.append((data, address, hora_recepcion))
        except socket.timeout:
            continue
    print("Terminando thread de recepcion {}".format(id))

def envio_th(sock, lock, caja, id):
    global finalizar_g
    print("Thread de envios {} inicializado\n".format(id))
    while(not finalizar_g):
        if(len(caja) > 0):
            ##########Podria mover esto a recepcion
            #Actualmente estoy recibiendo cualquier tipo de mensaje.
            #Al momento de usar los metodos de la clase paqueteNTP, esto puede levantarme una excepcion(error)
            #Si lo muevo a recepcion: Si me levanta excepcion, podria ignorar el mensaje completamente y continuar con la ejecucion.
            with lock:
                data, address, recvTime = caja.pop(0)
            recvNTP = paqueteNTP()
            recvNTP.decodificar(data)
            ##############################
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

            print(">> EnvID {0} Enviado a {1}".format(id,address))
            sock.sendto(sendNTP.codificar(), address)
        else:
            continue
    print("Terminando thread de envios {}".format(id))

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.settimeout(5)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("Servidor UDP levantado y escuchando.\nIP: {0}\nPuerto: {1}".format(localIP,localPort))

cerradura_recepcion = threading.Lock()
cerradura_envios = threading.Lock()

all_threads = list()
threads_recepcion = 1
threads_trabajo = 4

for x in range(threads_recepcion):      
    recepcion = threading.Thread(target=recepcion_th, args=(UDPServerSocket, cerradura_recepcion, box, x,))
    recepcion.start()
    all_threads.append(recepcion)

for x in range(threads_trabajo):
    envio = threading.Thread(target=envio_th, args=(UDPServerSocket, cerradura_envios, box, x,))
    envio.start()
    all_threads.append(envio)

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

