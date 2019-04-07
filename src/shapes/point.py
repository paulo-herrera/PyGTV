from ..helpers import _read_little_int, _read_big_int, _read_little_double, _read_big_double

class Point:
    
    shape_type = 1
    shape_desc = "Point"

    def __init__(self, idx, x, y): # a waste of memory, but makes easier to process shapes later
        self.idx     = idx
        self.points  = [(x,y)]
        self.npoints = 1
        self.parts   = [0]
        self.nparts  = 1
        self.bbox    = None

    def __str__(self):
        return "Point[%d]"%self.idx

    @staticmethod
    def read(b, verbose = False):
        if verbose: print("reading point...")
        # 0-3 	int32 	big 	Record number (1-based)
        idx = _read_big_int(b)
        if verbose: print("  idx: %d"%idx)

        # 4-7 	int32 	big 	Record length (in 16-bit words)
        length = _read_big_int(b)
        if verbose: print("  length: %d [bytes]"%length)

        shape_type = _read_little_int(b)
        assert shape_type == 1
        x = _read_little_double(b)
        y = _read_little_double(b)
        return Point(idx, x, y)
