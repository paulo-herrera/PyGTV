# Read content of a shape file (.shp) and creates a wrapper class to
# store its contents
# REFERENCE: ESRI Shapefile Technical Description

import struct
import binascii

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

class Point:
    
    shape_type = 1
    shape_desc = "Point"

    def __init__(self, idx, x, y): # a waste of memory, but makes easier to process shapes later
        self.idx     = idx
        self.points  = [(x,y)]
        self.npoints = 1
        self.parts   = [0]
        self.nparts  = 1

    def __str__(self):
        return "Point[%d]"%self.idx

    @staticmethod
    def read(b):
        print("reading point...")
        # 0-3 	int32 	big 	Record number (1-based)
        idx = _read_big_int(b)
        print("  idx: %d"%idx)

        # 4-7 	int32 	big 	Record length (in 16-bit words)
        length = _read_big_int(b)
        print("  length: %d [bytes]"%length)

        shape_type = _read_little_int(b)
        assert shape_type == 1
        x = _read_little_double(b)
        y = _read_little_double(b)
        return Point(idx, x, y)

class Polyline:

    shape_type = 3
    shape_desc = "Polyline"

    def __init__(self, idx, points, parts, bbox):
        self.idx    = idx
        self.points = points
        self.parts  = parts
        self.npoints = len(points)
        self.nparts  = len(parts)
        self.bbox = bbox

    def __str__(self):
        return "Polyline[%d]"%self.idx

    @staticmethod
    def read(b):
        print("reading polyline...")
        # 0-3 	int32 	big 	Record number (1-based)
        idx = _read_big_int(b)
        print("  idx: %d"%idx)

        # 4-7 	int32 	big 	Record length (in 16-bit words)
        length = _read_big_int(b)
        print("  length: %d [bytes]"%length)

        # 0-3 	int32 	little 	Shape type (see reference below)
        shape_type = _read_little_int(b)
        shape_desc = SHP_TYPES[shape_type]
        assert (shape_type == 3)
        print("  shape type: %d   desc: %s"%(shape_type, shape_desc))

        # 4 doubles with bounding box
        xmin, xmax, ymin, ymax = _read_bounding_box(b)
        bbox = (xmin, xmax, ymin, ymax)

        #
        numParts  = _read_little_int(b)
        numPoints = _read_little_int(b)
        print("  #parts: %d  #points: %d"%(numParts, numPoints))

        parts = []
        for i in range(numParts):
            p = _read_little_int(b)
            print("  parts: %d"%(p))
            parts.append(b)

        points = []
        for i in range(numPoints):
            x = _read_little_double(b)
            y = _read_little_double(b)
            print("  (x,y): (%g,%g)"%(x,y))
            points.append((x,y))

        return Polyline(idx, points, parts, bbox)

class Polygon:

    shape_type = 5
    shape_desc = "Polygon"

    def __init__(self, idx, points, parts, bbox):
        self.idx    = idx
        self.points = points
        self.parts  = parts
        self.npoints = len(points)
        self.nparts  = len(parts)
        self.bbox = bbox

    @staticmethod
    def read(b):
        print("reading polygon...")
        
        # 0-3 	int32 	big 	Record number (1-based)
        idx = _read_big_int(b)
        print("  idx: %d"%idx)

        # 4-7 	int32 	big 	Record length (in 16-bit words)
        length = _read_big_int(b) * 2
        print("  length: %d [bytes]"%length)
        
        # 0-3 	int32 	little 	Shape type (see reference below)
        shape_type = _read_little_int(b)
        shape_desc = SHP_TYPES[shape_type]
        assert (shape_type == 5)
        print("  shape type: %d   desc: %s"%(shape_type, shape_desc))
        
        # 4 doubles with bounding box
        xmin, xmax, ymin, ymax = _read_bounding_box(b)
        bbox = (xmin, xmax, ymin, ymax)
        print( "  (xmin, xmax, ymin, ymax): (%g,%g,%g,%g)"%bbox)
        
        #
        numParts  = _read_little_int(b)
        numPoints = _read_little_int(b)
        print("  #parts: %d  #points: %d"%(numParts, numPoints))

        parts = []
        for i in range(numParts):
            p = _read_little_int(b)
            print("  parts[i]: %d"%(p))
            parts.append(b)

        points = []
        for i in range(numPoints):
            x = _read_little_double(b)
            y = _read_little_double(b)
            print("  (x,y): (%g,%g)"%(x,y))
            points.append((x,y))

        return Polygon(idx, points, parts, bbox)
        
    def __str__(self):
        return "Polygon[%d]"%self.idx

class PolygonZ:

    shape_type = 15
    shape_desc = "PolygonZ"

    def __init__(self, idx, points, parts, bbox, mm, mpoints):
        self.idx    = idx
        self.points = points
        self.parts  = parts
        self.npoints = len(points)
        self.nparts  = len(parts)
        self.bbox = bbox
        self.mm = mm
        self.mpoints = mpoints

    @staticmethod
    def read(b):
        print("reading polygon...")
        
        # 0-3 	int32 	big 	Record number (1-based)
        idx = _read_big_int(b)
        print("  idx: %d"%idx)

        # 4-7 	int32 	big 	Record length (in 16-bit words)
        length = _read_big_int(b) * 2
        print("  length: %d [bytes]"%length)
        
        # 0-3 	int32 	little 	Shape type (see reference below)
        shape_type = _read_little_int(b)
        shape_desc = SHP_TYPES[shape_type]
        assert (shape_type == PolygonZ.shape_type)
        print("  shape type: %d   desc: %s"%(shape_type, shape_desc))
        
        # 4 doubles with bounding box
        xmin, xmax, ymin, ymax = _read_bounding_box(b)
        
        #
        numParts  = _read_little_int(b)
        numPoints = _read_little_int(b)
        print("  #parts: %d  #points: %d"%(numParts, numPoints))

        parts = []
        for i in range(numParts):
            p = _read_little_int(b)
            print("  parts[i]: %d"%(p))
            parts.append(b)

        pointsxy = []
        for i in range(numPoints):
            x = _read_little_double(b)
            y = _read_little_double(b)
            pointsxy.append((x,y))
        
        zmin = _read_little_double(b)
        zmax = _read_little_double(b)
        bbox = (xmin, xmax, ymin, ymax, zmin, zmax)
        print( "  (xmin, xmax, ymin, ymax, zmin, zmax): (%g,%g,%g,%g,%g,%g)"%bbox)
        
        pointsz = []
        for i in range(numPoints):
            z = _read_little_double(b)
            pointsz.append(z)
            
        mmin = _read_little_double(b)
        mmax = _read_little_double(b)
        mm = (mmin, mmax)
        
        mpoints = []
        for i in range(numPoints):
            m = _read_little_double(b)
            mpoints.append(m)
        
        points = []
        for i in range(len(pointsxy)):
            x, y, z = pointsxy[i][0], pointsxy[i][1], pointsz[i]
            print("  (x,y,z): (%g,%g,%g)"%(x,y,z))
            points.append((x,y,z))
            
        return PolygonZ(idx, points, parts, bbox, mm, mpoints)

    def __str__(self):
        return "PolygonZ[%d]"%self.idx
        
class ShapeFile:

    def __init__(self, shape_type, bbox, mm):
        """
        :param bbox: (xmin, xmax, ymin, ymax, zmin, zmax)
        :param mm: (mmin, mmax)
        """
        self.shape_type = shape_type
        self.shape_desc = SHP_TYPES[shape_type]
        self.bbox = bbox
        self.mm = mm # no idea what is this for
        self.shapes = []

    def add_shape(self, shape):
        assert self.shape_type == shape.shape_type
        self.shapes.append(shape)
        return self

    def print_shapes(self):
        for s in self.shapes:
            print(s)

    @staticmethod
    def _read_header(b):
        print("Reading header...")

        #0-3 int32 big File code (always hex value 0x0000270a)
        s = binascii.hexlify(bytearray(b.read(4)))
        assert (s == "0000270a"), s

        #4-23 	int32 	big 	Unused; five uint32
        b.read(20)

        #24-27 	int32 	big 	File length (in 16-bit words, including the header)
        length = _read_big_int(b) * 2  # size in bytes
        print("length[bytes]: + " + str(length) )

        #28-31 	int32 	little 	Version
        version = _read_little_int(b)
        assert (version == 1000)
        print("version: %d"%version)

        #32-35 	int32 	little 	Shape type (see reference below)
        shape_type = _read_little_int(b)
        shape_desc = SHP_TYPES[shape_type]
        print("shape type: %d   desc: %s"%(shape_type, shape_desc))

        #36-67 	double 	little 	Minimum bounding rectangle (MBR) of all shapes contained within the dataset; four doubles in the following order: min X, min Y, max X, max Y
        xmin, xmax, ymin, ymax = _read_bounding_box(b)

        #68-83 	double 	little 	Range of Z; two doubles in the following order: min Z, max Z
        zmin = _read_little_double(b)
        zmax = _read_little_double(b)
        bbox = (xmin, xmax, ymin, ymax, zmin, zmax)
        print( "(xmin, xmax, ymin, ymax, zmin, zmax): (%g,%g,%g,%g,%g,%g)"%bbox)

        #84-99 	double 	little 	Range of M; two doubles in the following order: min M, max M
        mmin = _read_little_double(b)
        mmax = _read_little_double(b)
        mm = (mmin, mmax)
        print("(mmin, mmax): (%g, %g)"%mm) # no clue what M values are for!!!

        return ShapeFile(shape_type, bbox, mm)

    @staticmethod
    def read(src):
        b = open(src, "rb") # assume shape file is not too large to fit in memory (in 2019!)

        # UGLY HACK TO CYCLE OVER SHAPES
        b.seek(0, 2)   # move to end of file
        eof = b.tell() # get current position
        b.seek(0, 0)   # go back to start of file

        shp = ShapeFile._read_header(b)

        shapes = []
        while (eof - b.tell()) > 0:
            # Read shapes
            if shp.shape_type == 0: # NULL
                b.read(8)       # read header data and skip
                s = None

            if shp.shape_type == 1:
                s = Point.read(b)

            elif shp.shape_type == 3:
                s = Polyline.read(b)
            
            elif shp.shape_type == 5:
                s = Polygon.read(b)
            
            elif shp.shape_type == 15:
                s = PolygonZ.read(b)
                
            else:
                assert False, "NOT IMPLEMENTED YET FOR TYPE: %d"%(shp.shape_type)

            shp.add_shape(s)
        b.close()
        return shp

if __name__ == "__main__":
    # read shape (.shp) files
    src = "/home/paulo/Desktop/PyGTV/src/examples/ex1/polygonz.shp"
    shp = ShapeFile.read(src)         # pass the pointer to the file. It could be faster to read it at once into memory.
    shp.print_shapes()
    print("*** ALL DONE ***")
