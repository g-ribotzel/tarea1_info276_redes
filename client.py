import socket
import inspect
from ntp import *

serverAddressPort   = ("172.25.40.131", 6000)
bufferSize          = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
sendNTP = NTPPacket()
UDPClientSocket.sendto(sendNTP.to_data(), serverAddressPort)
msgFromServer = UDPClientSocket.recvfrom(bufferSize)

recvNTP = NTPPacket()
recvNTP.from_data(msgFromServer[0])

#Inspeccion de clase
attributes = inspect.getmembers(recvNTP, lambda a:not(inspect.isroutine(a)))
msg = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
for x in msg:
    if(x[0]=='root_delay' or x[0]=='root_dispersion'):
        print(x[0], x[1]*(2**16))
    else:
        print(x)

#timeNTP = recvNTP.tx_timestamp_high + float(recvNTP.tx_timestamp_low) / 2 ** 32 - NTP.NTP_DELTA
timeNTP = recvNTP.tx_timestamp - NTP.NTP_DELTA

print(time.ctime(timeNTP).replace("  ", " "))

#while(True):
#    inputMsg = input("enter a message: ")
#    UDPClientSocket.sendto(inputMsg.encode(), serverAddressPort)
#    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
#    msg = "Message from Server {}".format(msgFromServer[0])
#    print(msg)