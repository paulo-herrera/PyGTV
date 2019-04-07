INTRODUCTION
============

Python Gis-to-Vtk (PyGTV) is a small python library to read and export vector GIS
information stored as shape (.shp) and associated (.dbf and .shx) files to VTK 
files that can be imported into visualization packages such as Paraview, VisIt 
or Mayavi.     

BACKGROUND
===========

Geographical Information Systems (GIS) store data in different formats. One of 
the most common format to store vector data is composed of 3 files (plus other 
optional ones):

   1. A shape file (.shp) that stores the geometry of the shapes (points, lines,
   polygons, etc). Each file can only store shapes of the same type, e.g. only 
   points, only lines, etc. Moreover, the initial format only stored plane 
   coordinates (x,y), but later modifications also include the z or elevation 
   coordinate (e.g. PointsZ variant).
   
   2. A database file (.dbf) that stores information related to shapes in the 
   .shp file. The information can be of different type: C (text), N or F (numeric),
   D (date), etc. The information for each shape is stored as a record that 
   contains multiple fields of different type, e.g. record = (id: Text, pressure: 
   Numeric, obs_date: Date, etc). QGis exports .dbf files in a dBase III format,
   which is a standard format for small databases.
   
   3. An index file (.shx) that stores information about the location of the data
   in the .dbf file, so it is possible to seek and retrieve information in random
   order without having to parse the file from the beginning, therefore avoiding 
   extra computational cost.

For the purposes of a library such as PyGTV only the two first files are important,
since the main objective is exporting the geometry and associated data without 
concern for optimization of the process. Thus, early versions of PyGTV only include
pure-Python parsers for the .shp and .dbf files, which are documented formats.

In addition to the 3 mandatory files, GIS software usually exports other files that
are important to interpret the data store in the .shp and/or .dbf files, for example
a projection file (.prj) that contains information about the geographical projection 
system used to define the coordinates of the geometric shapes. PyGTV exports this 
information as comments in the VTK file.

A main obstacle to export shape files to VTK is that the later does not have an option
for text data associated to grid elements, e.g. cells or lines. Hence, text data
(such as labels, ids, etc) can only be exported as comments that are included in 
the header section (XML) of the binary VTK files that are exported.

DOCUMENTATION:
==============

This file together with the included examples in the examples directory in the
source tree provide enough information to start using the package.
 
When the setup.py script is run, it installs scripts (e.g. shapeToVTK) in a bin 
directory that should be included in the PATH, so that they can be directly run from
the command line when python is also included in the PATH (typically, in Unix systems
such as Linux and/or Mac-OS). I have to test in Windows distributions such as
Anaconda.

The setup.py script also installs other files under the lib/ directory so that they
can be imported into other scripts or modules (see src/examples/points.py for an 
example).

REQUIREMENTS:
=============

    - Numpy. Tested with Numpy 1.8.0 to 1.13.3.
    - PyEVTK. Version 1.2.0 or higher.

It is compatible with both Python 2 (2.7+) and Python 3 (3.3+). 

DEVELOPER NOTES:
================

It is useful to build and install the package to a temporary location without
touching the global python site-packages directory while developing. To do
this, while in the root directory, one can type:

    1. python setup.py build --debug install --prefix=./tmp
    2. export PYTHONPATH=./tmp/lib/python2.7/site-packages/:$PYTHONPATH

NOTE: you may have to change the Python version depending of the installed
version on your system.

To test the package one can run some of the examples, e.g.:
./tmp/lib/python2.7/site-packages/gtv/examples/points.py

That should create a points.vtu file in the current directory.

I will continue releasing this package as open source, so it is free to be used 
in any kind of project. I will also continue providing support for simple questions 
and making incremental improvements as time allows. However, I also  provide 
contract based support for commercial or research projects interested in this 
package and/or I am open to discuss possible commercial licensing.

For further details, please contact me to: paulo.herrera.eirl@gmail.com.
