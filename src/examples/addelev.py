#################################################################
# Example of how to include elevation for an existing polygon   #
#################################################################

from gtv.files.shp import FileShp
from gtv.shapes.polygonz import PolygonZ
import sys
import os

if len(sys.argv) > 1:
    src = sys.argv[1]
    print("src: %s"%src)
else:
    PYGTV_DIR = os.environ['PYGTV_DIR']
    src = os.path.join(PYGTV_DIR, "src/examples/ex1/polygons.shp")
    
print("Shape source: " + src)

# Open existing shape file and reads point coordinates
fs = FileShp.read(src)
poly = fs.shapes[0]    # assume we want to use first polygon 
pts = poly.points

#--------------------------------------------------------------------------
# Replace this part if you want to modify z in another way
import random as rnd
ptsz = []
for p in pts:
    z = rnd.random()   # random in (0,1)
    xyz = (p[0], p[1], z)
    ptsz.append(xyz)
zmin = 0.0
zmax = 1.0
#--------------------------------------------------------------------------
bbox = (poly.bbox[0], poly.bbox[1], poly.bbox[2], poly.bbox[3], zmin, zmax)

# This part is to add additional data. See Tech. Specs. from ESRI for details.
mm = (0.0, 0.0)
mpoints = [0.0 for p in pts]

# Creates a new polygonZ to store elevation in addition to (x,y) coordinates
parts = [0]
polyz = PolygonZ(poly.idx, ptsz, parts, bbox, mm, mpoints)

# Create new file to store new polygon
# TODO: Change public interface of FileShp, so it is necessary to pass 
# the source when creating new files. For now, pass "CUSTOM" string
f = FileShp("CUSTOM", PolygonZ.shape_type, polyz.bbox, polyz.mm)
f.add_shape(polyz)

# Export to VTK file
fname = os.path.basename(src)
fname = fname.replace(".shp", "")
f.toVTK(fname)
print("PolygonZ exported to: " + fname + ".vtu")

print("*** ALL DONE ***")