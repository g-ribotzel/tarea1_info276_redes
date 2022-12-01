import struct
import datetime

#Codigo basado en https://github.com/limifly/ntpserver

SYSTEM_EPOCH = datetime.date(1970, 1, 1) #Tiempo 0 formato sistema
NTP_EPOCH = datetime.date(1900, 1, 1)    #Tiempo 0 formato NTP
NTP_DELTA = (SYSTEM_EPOCH - NTP_EPOCH).days * 24 * 3600 #Diferencia entre tiempo de sistema y tiempo NTP en segundos

#Transforma el tiempo de sistema a tiempo en formato NTP
def sysToNTP(timestamp):
    return timestamp + NTP_DELTA 

#Devuelve la parte entera de un tiempo en formato NTP
def toInt(timestamp):
    return int(timestamp)

#Devuelve la parte fraccionaria de n-bits del tiempo en formato NTP. n=32 por defecto.
def toFrac(timestamp, n=32):
    return int(abs(timestamp - toInt(timestamp)) * 2**n)

#Une la parte fraccionaria de n-bits y la parte entera para devolver un tiempo en NTP
def toTime(integ, frac, n=32):
    return integ + float(frac)/2**n	

#Error levantado por el modulo
class NTPException(Exception):
    pass

class paqueteNTP:
    #Formato del paquete al momento de codificar/decodificar
    _PACKET_FORMAT = "!B B B b 11I"

    def __init__(self, version=2, mode=3, tx_timestamp=0):
        self.leap = 0
        self.version = version
        self.mode = mode
        self.stratum = 0
        self.poll = 0
        self.precision = 0
        self.root_delay = 0
        self.root_dispersion = 0
        self.ref_id = 0

        #Tiempo de referencia
        self.ref_timestamp = 0
        self.ref_int = 0
        self.ref_frac = 0

        #Tiempo de origen
        self.orig_timestamp = 0
        self.orig_int = 0
        self.orig_frac = 0

        #Tiempo de recepcion
        self.recv_timestamp = 0
        self.recv_int = 0
        self.recv_frac = 0

        #Tiempo de transmision
        self.tx_timestamp = tx_timestamp
        self.tx_int = toInt(tx_timestamp)
        self.tx_frac = toFrac(tx_timestamp)

    def codificar(self):
        try:
            packed = struct.pack(paqueteNTP._PACKET_FORMAT,
                (self.leap << 6 | self.version << 3 | self.mode), #0
                self.stratum, #1
                self.poll, #2
                self.precision, #3
                toInt(self.root_delay) << 16 | toFrac(self.root_delay, 16), #4
                toInt(self.root_dispersion) << 16 | toFrac(self.root_dispersion, 16), #5 
                self.ref_id, #6 I
                self.ref_int, #7 Parte entera de referencia
                self.ref_frac, #8 Parte fraccionaria de referencia
                self.orig_int, #9 Parte entera de origen
                self.orig_frac, #10 Parte fraccionaria de origen
                self.recv_int, #11 Parte entera de recepcion
                self.recv_frac, #12 Parte fraccionaria de recepcion
                self.tx_int, #13 Parte entera de transmision
                self.tx_frac  #14 Parte fraccionaria de transmision
                )
        except struct.error:
            raise NTPException("Campos del paquete NTP invalidos.")
        return packed

    def decodificar(self, data):
        try:
            unpacked = struct.unpack(paqueteNTP._PACKET_FORMAT,
                    data[0:struct.calcsize(paqueteNTP._PACKET_FORMAT)])
        except struct.error:
            raise NTPException("Paquete NTP invalido.")

        self.leap = unpacked[0] >> 6 & 0x3
        self.version = unpacked[0] >> 3 & 0x7
        self.mode = unpacked[0] & 0x7
        self.stratum = unpacked[1]
        self.poll = unpacked[2]
        self.precision = unpacked[3]
        self.root_delay = float(unpacked[4])/2**16
        self.root_dispersion = float(unpacked[5])/2**16
        self.ref_id = unpacked[6]

        #self.ref_timestamp = toTime(unpacked[7], unpacked[8])
        self.ref_int = unpacked[7]
        self.ref_frac = unpacked[8]

        #self.orig_timestamp = toTime(unpacked[9], unpacked[10])
        self.orig_int = unpacked[9]
        self.orig_frac = unpacked[10]

        #self.recv_timestamp = toTime(unpacked[11], unpacked[12])
        self.recv_int = unpacked[11]
        self.recv_frac = unpacked[12]
        
        #self.tx_timestamp = toTime(unpacked[13], unpacked[14])
        self.tx_int = unpacked[13]
        self.tx_frac = unpacked[14]

        