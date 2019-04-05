from helpers import _read_little_int, _read_big_int, _read_little_double, _read_big_double, _read_bounding_box

class Multipoint:
    
    shape_type = 8
    shape_desc = "Multipoint"

    def __init__(self, idx, pts, bbox): # a waste of memory, but makes easier to process shapes later
        self.idx     = idx
        self.points  = pts
        self.npoints = len(pts)
        self.parts   = [0]
        self.nparts  = 1
        self.bbox    = None

    def __str__(self):
        return "Multipoint[%d]"%self.idx

    @staticmethod
    def read(b, verbose = False):
        if verbose: print("reading multipoint...")
        # 0-3 	int32 	big 	Record number (1-based)
        idx = _read_big_int(b)
        if verbose: print("  idx: %d"%idx)

        # 4-7 	int32 	big 	Record length (in 16-bit words)
        length = _read_big_int(b)
        if verbose: print("  length: %d [bytes]"%length)

        shape_type = _read_little_int(b)
        assert shape_type == 8
        xmin, xmax, ymin, ymax = _read_bounding_box(b)
        npoints = _read_little_int(b)
        pts = []
        for p in range(npoints):
            x = _read_little_double(b)
            y = _read_little_double(b)
            pts.append((x,y))
            
        return Multipoint(idx, pts, [xmin, xmax, ymin, ymax])
