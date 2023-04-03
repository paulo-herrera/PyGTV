import struct
import binascii
    
def _read_native_string(b, nbytes):
    bb = b.read(nbytes)
    #print(bb)
    s = bytearray(bb).decode('ASCII')
    #s = binascii.b2a_uu(bytearray(bb))
    #print(s)
    #print(len(bb))
    #s = struct.unpack("s", bytearray(bb))[0]
    return s

def _read_native_uchar(b):
    s = struct.unpack("b", bytearray(b.read(1)))[0]
    #s = s.decode("ascii")
    return s
    
def _read_native_char(b):
    s = struct.unpack("c", bytearray(b.read(1)))[0]
    s = s.decode("ascii")
    return s

def _read_native_short(b):
    return struct.unpack("h", bytearray(b.read(2)))[0]
    
def _read_native_ushort(b):
    return struct.unpack("H", bytearray(b.read(2)))[0]

def _read_native_int(b):
    return struct.unpack("i", bytearray(b.read(4)))[0]

def _read_native_uint(b):
    return struct.unpack("I", bytearray(b.read(4)))[0]
    
def _read_little_int(b):
    return struct.unpack("<i", bytearray(b.read(4)))[0]

def _read_big_int(b):
    return struct.unpack(">i", bytearray(b.read(4)))[0]

def _read_little_double(b):
    return struct.unpack("<d", bytearray(b.read(8)))[0]

def _read_big_double(b):
    return struct.unpack(">d", bytearray(b.read(8)))[0]

def _read_bounding_box(b):
    xmin = _read_little_double(b)
    ymin = _read_little_double(b)
    xmax = _read_little_double(b)
    ymax = _read_little_double(b)
    return xmin, xmax, ymin, ymax

