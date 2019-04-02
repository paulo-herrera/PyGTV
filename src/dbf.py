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
import datetime

from shapes.helpers import _read_little_int, _read_big_int, _read_little_double, _read_big_double
from shapes.helpers import _read_native_char, _read_native_ushort, _read_native_short
from shapes.helpers import _read_native_int, _read_native_uint, _read_native_string, _read_native_uchar

# TODO: Check for repeated field names

# NOTE: It seems that floating point numbers as marked as N or F. QGIS 3.6 always uses N
#       Date stored as YYYYMMDD
FIELD_TYPE = {          \
       "C" : "Text",    \
       "N" : "Number",  \
       "F" : "Float",   \
       "L" : "Logical", \
       "D" : "Date",    \
       "M" : "Memo" }

def print_record(pos, record):
    print(" Record: %d"%pos)
    for k in record.keys():
        print("  %d: (%s, %s)"%(k, record[k][0], record[k][1]))
            
class Field:
    
    def __init__(self, name, ftype, flength, fdecimal):
        """
        :param bsize: field size in bytes
        """
        self.name = name  # max 11 chars
        self.type = ftype
        self.type_desc = FIELD_TYPE[ftype]
        self.length = flength
        self.decimal = fdecimal
        
        # It seems QGIS exports every numeric field with the type N (which should be reserved for integers),
        # hence we set the type float for fields with decimal places > 0
        # THE SPEC IS NOT CLEAR ABOUT THIS POINT. KEEP IN MIND WHEN PARSING THE VALUES
        #if self.decimal > 0:
        #    self.type = "F"
        #    self.type_desc = FIELD_TYPE[self.type]
    
    def size(self):
        """ Returns size in bytes (or chars) for this field """
        return self.length
    
    def value(self, sstr):
        """ Return value of this field stored in string sstr """
        if self.type == "N" or self.type == "F":
            if self.decimal == 0:
                return int(sstr)
            else:
                return float(sstr)
        elif self.type == "D":
            return datetime.datetime.strptime(sstr, '%Y%m%d')
            #print("--- " + str(d) + " ---")
        elif self.type == "L": # QGIS DOES NOT GIVE THIS OPTION TO CREATE A FIELD
            return sstr
        elif self.type == "C":
            return sstr
        else:
            assert False, "Not recognized type"
        
    def __str__(self):
        s = "Field: %s\n"%self.name
        s = s + "  type[%s]: %s\n"%(self.type, self.type_desc)
        s = s + "  length: %d\n"%self.length 
        s = s + "  decimal: %d\n"%self.decimal
        return s

    @staticmethod
    def _read_field_descriptor(b):
        #0 10	11 bytes	Field name in ASCII (zero-filled)
        name = _read_native_string(b, 11).strip()
        #print(n)
        
        #11	1 byte	Field type in ASCII (C, D, F, L, M, or N)
        ftype = _read_native_char(b)
        #print(c)
        
        #1215	4 bytes	Reserved
        b.read(4)
        
        #16	1 byte	Field length in binary[note 1]
        flength = _read_native_uchar(b)
        #print(fl)
        
        #17	1 byte	Field decimal count in binary
        fdecimal = _read_native_uchar(b)
        #print(fd)
        
        #1819	2 bytes	Work area ID
        wid = _read_native_ushort(b)
        #print("wid: " + str(wid) )
        
        #20	1 byte	Example
        b.read(1)
        
        #2130	10 bytes	Reserved
        b.read(10)
        
        #31	1 byte	Production MDX field flag; 1 if field has an index tag in the production MDX file, 0 if not
        MDX = _read_native_uchar(b)
        assert (MDX == 0) or (MDX == 1)
        #print("MDX: " + str(MDX))
        
        return Field(name, ftype, flength, fdecimal)
    
class FileDbf:
    
    def __init__(self, src, fields, num_records, size_record):
        """
        :param src: full path to this file
        :param fields: list of Fields in the file 
        :param num_records: number of records in file
        :param size_record: size of each record in bytes
        """
        self.src = src
        self.fields = fields
        self.nfields = len(fields)
        self.num_records = num_records
        self.size_record = size_record
        self.records = []
    
    def display(self):
        print(self.__str__())
        #self.print_fields()
        self.print_records()
        
    def print_fields(self):
        for f in self.fields:
            print(f)
    
    def print_records(self):
        for r in range(self.num_records):
            print_record(r, self.records[r])
        
    def __str__(self):
        s = "FileDbf: \n"
        s = s + "  src: %s\n"%self.src
        s = s + "  # fields per record: %d\n"%len(self.fields)
        s = s + "  fields:\n"
        for f in self.fields:
            s = s + "    * %s: %s[%s] (%d characters) \n"%(f.name, f.type_desc, f.type, f.length)
        s = s + "  # records: %d\n"%self.num_records
        s = s + "  record size[bytes]: %d"%self.size_record
        return s
    
    def read_record(self, b, convert_str_to_values = True):
        """ Given a byte stream reads a record using the field description
            stored in self.fields """
        #http://web.archive.org/web/20150323061445/http://ulisse.elettra.trieste.it/services/doc/dbase/DBFstruct.htm#C1
        c = _read_native_char(b)    # space for not deleted, * for deleted
        #print("+++ " + c + " +++")
        
        r = {}
        for i in range(self.nfields):
            f = self.fields[i]
            #print("***" + f.name + "***")
            s = _read_native_string(b, f.size())
            
            # convert string to values
            if convert_str_to_values:
                v = f.value(s)
                r[i] = (f.name, v)
            else:
                r[i] = (f.name, s)
        
        self.records.append(r)
        return self
        
    @staticmethod
    def read(src, convert_records = True):
        """
            Reads a .dbf file and returns a FileDbf object that stores the
            list of fields and records as lists.
            
            :param src: path to .dbf file
            :param convert_records: If true convert strings to values in records
        """
        
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
        fields = []
        for f in range(nf):
            ff = Field._read_field_descriptor(b)
            fields.append(ff)
        
        fdbf = FileDbf(src, fields, nr, nbr)
        print(fdbf)
            
        #n +1	1 byte	0x0D as the field descriptor array terminator
        x = binascii.hexlify(bytearray(b.read(1)))
        assert x == "0d", x

        # read records
        for i in range(nr):
            fdbf.read_record(b, convert_records)
        
        b.close()
        
        return fdbf 

if __name__ == "__main__":
    #src = "/home/paulo/Desktop/PyGTV/src/examples/ex1/poly_lines.dbf"
    src = "/home/paulo/Documents/pyqgis/src/examples/ex1/poly_lines.dbf"
    
    fdbf = FileDbf.read(src, convert_records = False)
    fdbf.display()
        
    print("*** ALL DONE ***")
