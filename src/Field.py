FIELD_TYPE = { \
       "C" : "Text", \
       "N" : "Number", \
       "F" : "Floats", \
       "L" : "Logical", \
       "D" : "Date", \
       "M" : "Memo" }

class CField:
    _name = None
    _type = None
    _type_desc = None
    _length = None
    _decimal_length = None
    
    def __init__(self, field):
        """ Expects a field list with a list of attributes according to the following list: 
        """
        # FIELD_ATTRIB = { \
           # 0 : "Name", \
           # 1 : "Type", \
           # 2 : "Length", \
           # 3 : "Decimal length" }
        self._name = field[0]
        self._type = field[1]
        self._type_desc = FIELD_TYPE[self._type]
        self._length = field[2]
        self._decimal_length = field[3]

    def __str__(self):
        s = "Field: \n"
        s += "  - Name: %s\n"%(self._name)
        s += "  - Type: %s [%s]\n"%(self._type_desc, self._type)
        s += "  - Length: %s\n"%(self._length)
        s += "  - Decimal length: %s\n"%(self._decimal_length)
        return s
    
    @staticmethod
    def get_fields_dict(fields, verbose = False):
        """ Given a list of Fields, it returns a dictionary filled with keys that correspond to fields names, 
            but removing the keys that do not appear in the records database, e.g. DeletionFlag, etc 
        """
        if verbose:
            print("get_fields_dict...")
            
        ff = []
        for i in range(len(fields)):
            field = fields[i]
            if field._name != "DeletionFlag":
                ff.append(field)
                
        dict = {}
        for i in range(len(ff)):
            f = ff[i]
            if f._name != "DeletionFlag":
                dict[i] = f._name
        
        if verbose:
            for f in ff: print(str(f))
        
        return dict
        
# def print_field(field):
    # print("*"*30)
    # for i in range(4):
        # if i == 1:
            # str_t = FIELD_TYPE[field[i]]
            # print("%s: %s"%(FIELD_ATTRIB[i], field[i]))
            # print("Type desc: %s"%(str_t))
        # else:
            # print("%s: %s"%(FIELD_ATTRIB[i], field[i]))
    # print("*"*30)
