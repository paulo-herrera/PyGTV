from gtv.files.shp import FileShp
from gtv.files.dbf import FileDbf
import sys
import os

if len(sys.argv) > 1:
    src = sys.argv[1]
    print("src: %s"%src)
else:
    PYGTV_DIR = os.environ['PYGTV_DIR']
    src = os.path.join(PYGTV_DIR, "src/examples/ex1/points.shp")

dir = os.path.dirname(src)
src = os.path.basename(src)

if "." in src:
    root = src.split(".")[0]
    print("root: " + root) 
    src_shp = os.path.join(dir, root + ".shp")
    src_dbf = os.path.join(dir, root + ".dbf")
    
fs = FileShp.read(src_shp)
print(fs)

db = FileDbf.read(src_dbf)
print(db)

print("*"*25)
print("file: %s"%fs.src)
fs.list_shapes()

print("*"*25)
print("file: %s"%db.src)
db.print_fields()
print("*"*25)
print("file: %s"%db.src)
db.print_records()
print("*"*25)

vals, text = db.get_records_as_lists()

fs.add_attributes(db)
print("*"*25)
print("file: %s"%fs.src)
fs.list_shapes()

#print("*"*25)
#js = fs.asJSON()
#print(js)

print("*** ALL DONE ***")