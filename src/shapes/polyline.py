from shape_types import TS, SHP_TYPES
from helpers import _read_little_int, _read_big_int, _read_little_double, _read_big_double,  _read_bounding_box

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
