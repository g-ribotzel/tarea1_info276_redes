import threading
import socket
import time
from ntp import *

finalizar_g = False
box = list()
localIP     = "172.25.40.131"
localPort   = 6000

def recepcion_th(sock, caja):
    global finalizar_g
    print("Thread de recepcion inicializado")
    while(not finalizar_g):
        try:
            data, address = sock.recvfrom(1024)
            hora_recepcion = time.time()
            print("RECEPCION > {0} \nTiempo: {1}".format((data,address), hora_recepcion))
            caja.append((data, address, hora_recepcion))
        except socket.timeout:
            continue
    print("Terminando thread de recepcion")

def envio_th(sock, caja):
    global finalizar_g
    print("Thread de envios inicializado")
    while(not finalizar_g):
        if(len(caja) > 0):
            data, address, recvTime = caja.pop(0)
            recvNTP = NTPPacket()
            recvNTP.from_data(data)

            if(recvNTP.mode == 3):
                sendNTP = NTPPacket(mode=4)
            else:
                sendNTP = NTPPacket(mode=2)
            
            sendNTP.stratum = 2
            sendNTP.poll = recvNTP.poll
            sendNTP.tx_timestamp = sendNTP.ref_timestamp = sendNTP.recv_timestamp = system_to_ntp_time(recvTime)
            sendNTP.orig_timestamp = recvNTP.orig_timestamp

            sock.sendto(sendNTP.to_data(), address)
        else:
            continue
    print("Terminando thread de envios")

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.settimeout(5)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("Servidor UDP levantado y escuchando")

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

