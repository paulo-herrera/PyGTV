import shapefile
from evtk.hl import pointsToVTK, polyLinesToVTK, unstructuredGridToVTK
from evtk.vtk import VtkPolygon
from Field import CField

SHP_TYPES = {  \
          0 : "NULL", \
          1 : "POINT", \
          3 : "POLYLINE",\
          5 : "POLYGON", \
          8 : "MULTIPOINT", \
         11 : "POINTZ", \
         13 : "POLYLINEZ", \
         15 : "POLYGONZ", \
         18 : "MULTIPOINTZ", \
         21 : "POINTM", \
         23 : "POLYLINEM", \
         25 : "POLYGONM", \
         28 : "MULTIPOINTM", \
         31 : "MULTIPATCH" }
         
def get_fields_list(src, verbose = False):
    """ Returns a dictionary with the fields that are associated to each shape. 
        :param src: a file-like object as returned by shapefile.Reader
    """
    if verbose: 
        print("Fields: ")
    
    fields = []
    for i in range(len(src.fields)):
        fields.append( CField(src.fields[i]) )
        
    return fields 

def get_shapes_list(src, verbose = False):
    """ Returns a list of shapes in the reader.
        :param src: a file-like object as returned by shapefile.Reader
    """
    shapes = []
    _shapes = src.shapes()
    for i in range(len(_shapes)):
        shapes.append(CShape(i, _shapes[i]))
        
    return shapes

def get_records_list(src, verbose = False):
    """ Returns a list of records (defined by the fields list) associated to each shape in the file.
        :param src: a file-like object as returned by shapefile.Reader
    """
    if verbose: print("Records list: ")
    return src.records()

class CShape:       
    
    def __init__(self, idx, sh):
        # TODO: Check if any of the arguments is NULL or None
        self._idx = idx                                # index in shape list
        self._type = sh.shapeType                      # type as an integer
        self._desc_type = SHP_TYPES[self._type]        # type description
        self._points = sh.points                       # list of points that defines this shape
        self._fields = {}            # field associated to each shape that are stored as records
        self._attrib = {}            # consider to drop. Only real use is for printing  
        
        # Consider to drop _attrib after adding bbox since it does not contain any important information.
        for attr, value in sh.__dict__.items():
            #print(attr, value)
            self._attrib[attr] =  value
        
        if "bbox" in self._attrib.keys(): 
            self._bbox = self._attrib["bbox"]    # lower and upper corners
        
    def __str__(self):
        s = "Shape[%d]: %s\n"%(self._idx, self._desc_type)
        # THINK IF ADDING THESE ATTRIBS MAKE SENSE
        for attr, value in self._attrib.items():
            # #print(attr, value)
            s += "  - %s: %s\n"%(attr, value)
        
        s += "  Fields: \n"
        for k,f in self._fields.items():
            s += "    + %s: %s \n"%(k, f)
        
        return s
        
    def add_fields(self, fields_dict, record):
        #print("add_fields")
        keys = sorted(fields_dict.keys())
        for k in keys:
            #print(k)
            name = fields_dict[k]
            self._fields[name] = record[k]
        #print("--- add_fields")
    
    def _create_points_list(self, DEBUG = False, default_z = 0.0):
        # list of point coordinate
        self._x, self._y, self._z = [], [], [] 
        for p in self._points:
            if DEBUG: print(p)
            self._x.append(p[0])
            self._y.append(p[1])
            self._z.append(default_z)   # check for polyz type
        
        self._pointsPerShape = len(self._points )
    
    @staticmethod
    def readShapes(src, verbose = False):
        sf = shapefile.Reader(src)

        shapes  = get_shapes_list(sf, verbose)
        fields  = get_fields_list(sf, verbose)
        records = get_records_list(sf, verbose)
        # close Reader. CHECK FOR METHOD TO CLOSE THE READER FILE
        
        # Assign properties to shapes 
        fields_dict = CField.get_fields_dict(fields)
        if verbose:
            for k in fields_dict.keys(): 
                print("%s, %s"%(k, fields_dict[k]))

        assert len(shapes) == len(records)
        for i in range(len(shapes)):
            shapes[i].add_fields(fields_dict, records[i])

        if verbose:
            for s in shapes: print(s)

        return shapes
        
    @staticmethod
    def toVTK(dst, shapes, verbose = False):
        nshapes = len(shapes)
        x, y, z = [], [], []
        pointsPerShape = []
        
        # CHECK WHEN IT MAKES SENSE TO ADD POINT DATA OR CELL DATA
        ppointData = {}
        
        ccellData = {}   #
        ccellData["ids"] = []   # Index for each shape
        # Initialize other fields list
        if verbose:
            print(40*"-")
            print("Initialize fields for shapes")

            for f in shapes[0]._fields:
                if verbose: print(f)
                ccellData[f] = []
        
        if verbose: print(40*"-")
        
        for s in shapes:
            ccellData["ids"].append(s._idx)
            s._create_points_list()
            
            #for i in range(len(s._x)):
            #    print("%d: (%f,%f,%f)"%(i, s._x[i], s._y[i], s._z[i]))
                       
            x = x + s._x
            y = y + s._y
            z = z + s._z
            
            #print(len(x))
            pointsPerShape.append(s._pointsPerShape)
            
            for f in s._fields.keys():
                value = s._fields[f]
                ccellData[f].append(value)
        
        if verbose:
            for s in shapes:
                print("Shape: %d"%s._idx)
                print("# points in file: %d"%len(s._x))
                print("s._pointsPerShape: %d"%(s._pointsPerShape))
                
        import numpy as np
        x = np.array(x)
        y = np.array(y)
        z = np.array(z)
         
        pointsPerShape = np.array(pointsPerShape)
        #print("pointsPerShape: " + str(pointsPerShape))
        #print("pointsPerLine: " + str(pointsPerLine))
        #print("len(x): %d"%len(x))
        
        # JUST ADD SOME INTELLIGENT LOGIC HERE TO EXPORT TO VTK ACCORDING TO THE SHAPE TYPE...
        cellData = {}
        for k in ccellData.keys():
            c = ccellData[k]
            cellData[k] = np.array(c)
        
        print("+"*80)
        for k,c in cellData.items():
            print("%s: %d"%(k, len(c))) 
        cellData.pop("desc") # HAVE TO REMOVE TEXT FIELDS THAT CANNOT BE EXPORTED TO VTK FILES
        print("+"*80)
        
        pointData = {}   # CHECK WHEN IT MAKES SENSE TO ADD POINT DATA OR CELL DATA
        for k in pointData.keys():
            c = ppointData[k]
            pointData[k] = np.array(c)
        
        type = shapes[0]._type
        if verbose:
            print("type (%d): %s"%(type, SHP_TYPES[type]) )
        
        if type == 1 or type == 8:    # POINT
            pointsToVTK(dst, x, y, z, data = cellData)
            
        elif type == 3:  # POLYLINE 
            polyLinesToVTK(dst, x, y, z, pointsPerLine = pointsPerShape, cellData = cellData, pointData = pointData)
            
        elif type == 5:  # POLYGON
            
            # Points should be counter clock-wise
            # Add a small check LATER
            conn   = np.array([i for i in range(len(x))])
            offsets = np.zeros(nshapes) 
            cell_types = np.ones(nshapes) * VtkPolygon.tid 
            o = 0
            for s in range(nshapes):
                o = o + pointsPerShape[s]
                offsets[s] = o
                unstructuredGridToVTK(dst, x, y, z, conn, offsets, cell_types, cellData = cellData, pointData = pointData)
        else:
            assert False, "Not implemented for type %d"%type

# def print_shape(shp):
    # #print(sh.shapeTypeName)
    # print("-"*30)

    # t = SHP_TYPES[shp.shapeType]
    # print("Shape: %s"%(t) )
    # for attr, value in shp.__dict__.items():
        # print(attr, value)
    # print("-"*30) 
    