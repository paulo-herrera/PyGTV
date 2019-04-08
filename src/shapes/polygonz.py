from shape_types import TS, SHP_TYPES
from ..helpers import _read_little_int, _read_big_int, _read_little_double, _read_big_double, _read_bounding_box
from .shape import Shape

class PolygonZ(Shape):

    shape_type = 15
    shape_desc = "PolygonZ"

    def __init__(self, idx, points, parts, bbox, mm, mpoints):
        Shape.__init__(self)
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
        s = "PolygonZ[%d]\n"%self.idx
        s = s + Shape.__str__(self)
        return s
