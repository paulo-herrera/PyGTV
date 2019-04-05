from shape_types import TS, SHP_TYPES
from helpers import _read_little_int, _read_big_int, _read_little_double, _read_big_double, _read_bounding_box

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
        
    # TODO: REMOVE BUGS LATER
    @staticmethod
    def read(b, verbose = False):
        if verbose: print("reading polygon...")
        
        # 0-3 	int32 	big 	Record number (1-based)
        idx = _read_big_int(b)
        if verbose: print("  idx: %d"%idx)

        # 4-7 	int32 	big 	Record length (in 16-bit words)
        length = _read_big_int(b) * 2
        if verbose: print("  length: %d [bytes]"%length)
        
        # 0-3 	int32 	little 	Shape type (see reference below)
        shape_type = _read_little_int(b)
        shape_desc = SHP_TYPES[shape_type]
        assert (shape_type == 5)
        if verbose: print("  shape type: %d   desc: %s"%(shape_type, shape_desc))
        
        # 4 doubles with bounding box
        xmin, xmax, ymin, ymax = _read_bounding_box(b)
        bbox = (xmin, xmax, ymin, ymax)
        if verbose: print( "  (xmin, xmax, ymin, ymax): (%g,%g,%g,%g)"%bbox)
        
        #
        numParts  = _read_little_int(b)
        numPoints = _read_little_int(b)
        if verbose: print("  #parts: %d  #points: %d"%(numParts, numPoints))

        parts = []
        for i in range(numParts):
            p = _read_little_int(b)
            if verbose: print("  parts[i]: %d"%(p))
            parts.append(b)

        points = []
        for i in range(numPoints):
            x = _read_little_double(b)
            y = _read_little_double(b)
            if verbose: print("  (x,y): (%g,%g)"%(x,y))
            points.append((x,y))

        return Polygon(idx, points, parts, bbox)
        
    def __str__(self):
        return "Polygon[%d]"%self.idx
