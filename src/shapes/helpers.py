import struct

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

