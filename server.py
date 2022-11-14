import threading
import socket
import time
import inspect
from ntp import *

finalizar_g = False
box = list()
localIP     = "172.25.40.131"
localPort   = 6000

def recepcion_th(sock, caja):
    global finalizar_g
    print("Thread de recepcion inicializado\n")
    while(not finalizar_g):
        try:
            data, address = sock.recvfrom(1024)
            hora_recepcion = time.time()
            print("RECEPCION DESDE > {}".format(address))
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
            recvNTP = NTPPacket()
            recvNTP.from_data(data)
            timeStamp_high,timeStamp_low = recvNTP.GetTxTimeStamp()

            if(recvNTP.mode == 3):
                sendNTP = NTPPacket(mode=4)
            else:
                sendNTP = NTPPacket(mode=2)
            
            sendNTP.stratum = 2
            sendNTP.poll = recvNTP.poll 
            
            sendNTP.orig_timestamp = toTime(timeStamp_high,timeStamp_low)       
            sendNTP.SetOriginTimeStamp(timeStamp_high,timeStamp_low)

            sendNTP.tx_timestamp = sendNTP.ref_timestamp = sendNTP.recv_timestamp = sysToNTP(recvTime)
            sendNTP.tx_timestamp_high = toInt(sendNTP.tx_timestamp)
            sendNTP.tx_timestamp_low = toFrac(sendNTP.tx_timestamp)

            sock.sendto(sendNTP.to_data(), address)

            #Inspeccion de clase
            attributes = inspect.getmembers(sendNTP, lambda a:not(inspect.isroutine(a)))
            msg = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
            print(*msg, sep="\n")
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
        print("Exiting...")

        finalizar_g = True
        recepcion.join()
        envio.join()

        UDPServerSocket.close()
        print("Exited")
        break

