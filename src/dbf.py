# Implements a simple DBF IV parser to read records stored as .dbf files.
# Author: Paulo Herrera R.
# Data: 01/April/2019
# REFERENCE: 
#    - http://www.independent-software.com/dbase-dbf-dbt-file-format.html
#    - http://web.archive.org/web/20150323061445/http://ulisse.elettra.trieste.it/services/doc/dbase/DBFstruct.htm
#
# File structure:
# - Header
# - List of field descriptors
# - List of records
# 
# The file created by QGIS seems to follow the dBase III format
########################################################################

import struct
import binascii

from shapes.helpers import _read_little_int, _read_big_int, _read_little_double, _read_big_double
from shapes.helpers import _read_native_char, _read_native_ushort, _read_native_short
from shapes.helpers import _read_native_int, _read_native_uint, _read_native_string, _read_native_uchar

def _read_field_descriptor(b):
    #0 10	11 bytes	Field name in ASCII (zero-filled)
    n = _read_native_string(b, 11)
    print(n.strip())
    
    #11	1 byte	Field type in ASCII (C, D, F, L, M, or N)
    c = _read_native_char(b)
    print(c)
    
    #1215	4 bytes	Reserved
    b.read(4)
    
    #16	1 byte	Field length in binary[note 1]
    fl = _read_native_uchar(b)
    print(fl)
    
    #17	1 byte	Field decimal count in binary
    fd = _read_native_uchar(b)
    print(fd)
    
    #1819	2 bytes	Work area ID
    wid = _read_native_ushort(b)
    print("wid: " + str(wid) )
    
    #20	1 byte	Example
    b.read(1)
    
    #2130	10 bytes	Reserved
    b.read(10)
    
    #31	1 byte	Production MDX field flag; 1 if field has an index tag in the production MDX file, 0 if not
    MDX = _read_native_uchar(b)
    assert (MDX == 0) or (MDX == 1)
    print("MDX: " + str(MDX))

#src = "/home/paulo/Desktop/PyGTV/src/examples/ex1/poly_lines.dbf"
src = "/home/paulo/Documents/pyqgis/src/examples/ex1/poly_lines.dbf"

b = open(src, "rb")
#0	1 byte	Valid dBASE for DOS file; bits 0-2 indicate version number, bit 3 indicates the presence of a dBASE for DOS memo file, bits 4-6 indicate the presence of a SQL table, bit 7 indicates the presence of any memo file (either dBASE m PLUS or dBASE for DOS)
ver = binascii.hexlify(bytearray(b.read(1)))
assert ver == "03"
print("Version: " + str(ver))

#1-3	3 bytes	Date of last update; formatted as YYMMDD
b.read(3)
#print(d.decode("ascii"))

#4-7	32-bit number	Number of records in the database file
nr = _read_native_uint(b)
print("nr: %d"%nr)

# 8-9	16-bit number	Number of bytes in the header
nbh = _read_native_ushort(b)
print("nbh: " + str(nbh))
print("nbh - 32 - 1: " + str(nbh - 32 - 1)) # 32 bytes header + 1 byte end of header
nf = int( (nbh - 33) / 32) # Each field descriptor has 32 bytes
print("nf: " + str(nf))

#10-11	16-bit number	Number of bytes in the record
nbr = _read_native_ushort(b)
print("nbr: " + str(nbr))

#12-13	2 bytes	Reserved; fill with 0
b.read(2)

#14	1 byte	Flag indicating incomplete transaction[note 1]
b.read(1)

#15	1 byte	Encryption flag[note 2]
b.read(1)

#16-27	12 bytes	Reserved for dBASE for DOS in a multi-user environment
b.read(12)

# 28	1 byte	Production .mdx file flag; 0x01 if there is a production .mdx file, 0x00 if not
b.read(1)

#29	1 byte	Language driver ID
b.read(1)

#30-31	2 bytes	Reserved; fill with 0
b.read(2)

#32-n[note 3][note 4]	32 bytes each	Field descriptor array (the structure of this array is shown in Table Database field descriptor bytes)
for f in range(nf):
    _read_field_descriptor(b)


#n +1	1 byte	0x0D as the field descriptor array terminator
x = binascii.hexlify(bytearray(b.read(1)))
assert x == "0d", x

b.close()

print("*** ALL DONE ***")
