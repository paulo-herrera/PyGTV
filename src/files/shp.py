# Read content of a shape file (.shp) and creates a wrapper class to
# store its contents
# REFERENCE: ESRI FileShp Technical Description

import struct
import binascii

from ..helpers import _read_little_int, _read_big_int, _read_little_double, _read_big_double, _read_bounding_box
from ..shapes.shape_types import TS, SHP_TYPES
from ..shapes.point import Point
from ..shapes.polyline import Polyline
from ..shapes.polygon import Polygon
from ..shapes.polygonz import PolygonZ
from ..shapes.multipoint import Multipoint

# ONLY USED FOR JSON SERIALIZATION
def jdefault(o):
    import datetime
    if isinstance(o, datetime.datetime):
        return str(o)
    return o.__dict__
            
class FileShp:
    def __init__(self, src, shape_type, bbox, mm):
        """
        :param bbox: (xmin, xmax, ymin, ymax, zmin, zmax)
        :param mm: (mmin, mmax)
        """
        self.src = src
        self.shape_type = shape_type
        self.shape_desc = SHP_TYPES[shape_type]
        self.bbox = bbox
        self.mm = mm # no idea what is this for
        self.shapes = []
    
    def __str__(self):
        s = "="*40 + "\n"
        s = s + "Shape file (.shp): \n"
        s = s + "  - Src: " + self.src + "\n"
        s = s + "  - Type: " + self.shape_desc + "\n"
        s = s + "  - # shapes: " + str(len(self.shapes)) + "\n"
        s = s + "="*40
        return s
        
    def add_shape(self, shape):
        assert self.shape_type == shape.shape_type
        self.shapes.append(shape)
        return self

    def list_shapes(self):
        for s in self.shapes:
            print(s)

    def get_xyz_lists(self, default_z = None, verbose = False):
        if not default_z: 
            default_z = self.bbox[4] #zmin
        
        # list of point coordinates
        x, y, z = [], [], []
        pointsPerShape = []
        
        for s in self.shapes:
            for p in s.points:
                if verbose: print(p)
                x.append(p[0])
                y.append(p[1])
                if self.shape_type < 11:
                    z.append(default_z)
                elif self.shape_type >= 11 and self.shape_type <= 18:                   # check for polyz type
                    z.append(p[2])
            pointsPerShape.append(s.npoints)
            
        return x, y, z, pointsPerShape
    
    def add_attributes(self, dbf):
        """ Given a dbf file, add the records in the file as attributes to the 
            shapes stored in this file. It makes easier to work with shapes and records. 
        """
        rec = dbf.get_records()
        assert len(rec) == len(self.shapes)
        for s in range(len(self.shapes)):
            shape = self.shapes[s]
            shape.add_attributes(rec[s])
        
    # TODO: Check if the exported file makes sense!
    def toVTK(self, dst, vals = None, text = None , default_z = None, verbose = False, comments = None):
        from evtk.hl import pointsToVTK, polyLinesToVTK, unstructuredGridToVTK
        from evtk.vtk import VtkPolygon
        
        x, y, z, pointsPerShape = self.get_xyz_lists(default_z, verbose)
        nshapes = len(self.shapes)
        
        import numpy as np
        x = np.array(x)
        y = np.array(y)
        z = np.array(z)
        pointsPerShape = np.array(pointsPerShape)
        
        # Export cell data
        if vals:
            cellData = {}
            for k, v in vals.items():
                cellData[k] = np.array(v)
        else:
            cellData = None
        
        #for k, v in cellData.items():
            #print(k, v)
        
        if comments:
            pass
        else:
            comments = []
            
        if text:
            comments.append("Text fields as lists with one element for each shape follows...")
            for k, v in text.items():
                cmt = "%s: "%k + "[" + ",".join(v) + "]"
                #print(cmt)
                comments.append(cmt)
        else:
            comments = None
        
        if verbose:
            print("type (%d): %s"%(self.shape_type, SHP_TYPES[type]) )
        
        st = self.shape_type
        if st == TS["POINT"] or st == TS["POINTZ"]:          # POINT
            pointsToVTK(dst, x, y, z, data = cellData, comments = comments)

        elif st == TS["MULTIPOINT"]:                          # MULTIPOINT
            pointsToVTK(dst, x, y, z, data = cellData, comments = comments)
            
        elif st == TS["POLYLINE"] or st == TS["POLYLINEZ"]:  # POLYLINE
            polyLinesToVTK(dst, x, y, z, pointsPerLine = pointsPerShape, cellData = None, pointData = None)

        elif st == TS["POLYGON"] or st == TS["POLYGONZ"]:    # POLYGON

            # Points should be counter clock-wise
            # Add a small check LATER
            conn   = np.array([i for i in range(len(x))])
            offsets = np.zeros(nshapes)
            cell_types = np.ones(nshapes) * VtkPolygon.tid
            o = 0
            for s in range(nshapes):
                o = o + pointsPerShape[s]
                offsets[s] = o
                unstructuredGridToVTK(dst, x, y, z, conn, offsets, cell_types, cellData = cellData, pointData = None, comments = comments)
        else:
            assert False, "Not implemented for type %d"%st
        
    @staticmethod
    def _read_header(b, src, verbose = False):
        print("Reading header...")

        #0-3 int32 big File code (always hex value 0x0000270a)
        s = binascii.hexlify(bytearray(b.read(4)))
        assert (s == "0000270a"), s

        #4-23 	int32 	big 	Unused; five uint32
        b.read(20)

        #24-27 	int32 	big 	File length (in 16-bit words, including the header)
        length = _read_big_int(b) * 2  # size in bytes
        if verbose: print("length[bytes]: + " + str(length) )

        #28-31 	int32 	little 	Version
        version = _read_little_int(b)
        assert (version == 1000)
        if verbose: print("version: %d"%version)

        #32-35 	int32 	little 	Shape type (see reference below)
        shape_type = _read_little_int(b)
        shape_desc = SHP_TYPES[shape_type]
        if verbose: print("shape type: %d   desc: %s"%(shape_type, shape_desc))

        #36-67 	double 	little 	Minimum bounding rectangle (MBR) of all shapes contained within the dataset; four doubles in the following order: min X, min Y, max X, max Y
        xmin, xmax, ymin, ymax = _read_bounding_box(b)

        #68-83 	double 	little 	Range of Z; two doubles in the following order: min Z, max Z
        zmin = _read_little_double(b)
        zmax = _read_little_double(b)
        bbox = (xmin, xmax, ymin, ymax, zmin, zmax)
        if verbose: print( "(xmin, xmax, ymin, ymax, zmin, zmax): (%g,%g,%g,%g,%g,%g)"%bbox)

        #84-99 	double 	little 	Range of M; two doubles in the following order: min M, max M
        mmin = _read_little_double(b)
        mmax = _read_little_double(b)
        mm = (mmin, mmax)
        if verbose: print("(mmin, mmax): (%g, %g)"%mm) # no clue what M values are for!!!

        return FileShp(src, shape_type, bbox, mm)

    @staticmethod
    def read(src, verbose = False):
        print("Reading .shp file from: ")
        print(src)
        
        b = open(src, "rb") # assume shape file is not too large to fit in memory (in 2019!)

        # UGLY HACK TO CYCLE OVER SHAPES
        b.seek(0, 2)   # move to end of file
        eof = b.tell() # get current position
        b.seek(0, 0)   # go back to start of file

        shp = FileShp._read_header(b, src, verbose)

        shapes = []
        while (eof - b.tell()) > 0:
            # Read shapes
            if shp.shape_type == 0: # NULL
                b.read(8)           # read header data and skip
                s = None

            if shp.shape_type == TS["POINT"]:
                s = Point.read(b)
            
            elif shp.shape_type == TS["MULTIPOINT"]:
                s = Multipoint.read(b)
                
            elif shp.shape_type == TS["POLYLINE"]:
                s = Polyline.read(b)
            
            elif shp.shape_type == TS["POLYGON"]:
                s = Polygon.read(b)
            
            elif shp.shape_type == TS["POLYGONZ"]:
                s = PolygonZ.read(b)
                
            else:
                assert False, "NOT IMPLEMENTED YET FOR TYPE: %d"%(shp.shape_type)

            shp.add_shape(s)
        b.close()
        return shp
        
    def asJSON(self):
        """ Returns string with information stored in this file in JSON format.
        """
        import json
    
        jsonString  = json.dumps(self, default=jdefault, indent=4, sort_keys=False)
        return jsonString

if __name__ == "__main__": 
    from dbf import FileDbf
    from prj import FilePrj
    import os
    
    # read shape (.shp) files
    #src = "/home/paulo/Desktop/PyGTV/src/examples/ex1/poly_lines.shp"
    src = r"/home/paulo/Documents/pyqgis/src/examples/ex1/polygons.shp"
    dst = "/home/paulo/Documents/pyqgis/vtk/polygons"
    shp = FileShp.read(src, verbose = False)         # pass the pointer to the file. It could be faster to read it at once into memory.
    print(shp)
    #shp.list_shapes()
    
    src_dbf = src.split(".")[0] + ".dbf"
    dbf = FileDbf.read(src_dbf)
    #print(dbf)
    
    src_prj = src.split(".")[0] + ".prj"
    prj = FilePrj.read(src_prj)
    #print(prj)
    
    vals, text = dbf.get_records_as_lists()
    comments = [".shp: " + shp.src]
    comments = comments + [".dbf: " + dbf.src]
    comments = comments + [".prj: " + prj.src]
    shp.toVTK(dst, vals = vals, text = text, comments = comments)
    print("*** ALL DONE ***")
