import struct
import datetime

#Recreacion de codigo NTP extraido de Github

SYSTEM_EPOCH = datetime.date(1970, 1, 1)
"""system epoch"""
NTP_EPOCH = datetime.date(1900, 1, 1)
"""NTP epoch"""
NTP_DELTA = (SYSTEM_EPOCH - NTP_EPOCH).days * 24 * 3600
"""delta between system and NTP time"""

def sysToNTP(timestamp):
    """Convert a system time to a NTP time.

    Parameters:
    timestamp -- timestamp in system time

    Returns:
    corresponding NTP time
    """
    return timestamp + NTP_DELTA

def toInt(timestamp):
    """Return the integral part of a timestamp.

    Parameters:
    timestamp -- NTP timestamp

    Retuns:
    integral part
    """
    return int(timestamp)

def toFrac(timestamp, n=32):
    """Return the fractional part of a timestamp.

    Parameters:
    timestamp -- NTP timestamp
    n         -- number of bits of the fractional part

    Retuns:
    fractional part
    """
    return int(abs(timestamp - toInt(timestamp)) * 2**n)

def toTime(integ, frac, n=32):
    """Return a timestamp from an integral and fractional part.

    Parameters:
    integ -- integral part
    frac  -- fractional part
    n     -- number of bits of the fractional part

    Retuns:
    timestamp
    """
    return integ + float(frac)/2**n	

class NTPException(Exception):
    """Exception raised by this module."""
    pass

class paqueteNTP:
    _PACKET_FORMAT = "!B B B b 11I"
    """packet format to pack/unpack"""

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

        self.ref_timestamp = 0
        self.ref_int = 0
        self.ref_frac = 0
        """reference timestamp"""
        self.orig_timestamp = 0
        self.orig_int = 0
        self.orig_frac = 0
        """originate timestamp"""
        self.recv_timestamp = 0
        self.recv_int = 0
        self.recv_frac = 0
        """receive timestamp"""
        self.tx_timestamp = tx_timestamp
        self.tx_int = toInt(tx_timestamp)
        self.tx_frac = toFrac(tx_timestamp)
        """tansmit timestamp"""

    def codificar(self):
        try:
            packed = struct.pack(paqueteNTP._PACKET_FORMAT,
                (self.leap << 6 | self.version << 3 | self.mode), #0 !B
                self.stratum, #1 B
                self.poll, #2 B
                self.precision, #3 b
                toInt(self.root_delay) << 16 | toFrac(self.root_delay, 16), #4 I
                toInt(self.root_dispersion) << 16 | toFrac(self.root_dispersion, 16), #5 I
                self.ref_id, #6 I
                self.ref_int, #7 Parte entera de referencia 
                self.ref_frac, #8 Parte fraccionaria
                self.orig_int, #9 Parte entera de origen
                self.orig_frac, #10 Parte fraccionaria
                self.recv_int, #11 Parte entera de recepcion
                self.recv_frac, #12 Parte fraccionaria
                self.tx_int, #13 Parte entera de transmision
                self.tx_frac  #14 Parte fraccionaria
                )
        except struct.error:
            raise NTPException("Invalid NTP packet fields.")
        return packed

    def decodificar(self, data):
        try:
            unpacked = struct.unpack(paqueteNTP._PACKET_FORMAT,
                    data[0:struct.calcsize(paqueteNTP._PACKET_FORMAT)])
        except struct.error:
            raise NTPException("Invalid NTP packet.")

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

        