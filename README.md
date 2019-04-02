Background
===========

Geographical Information Systems (GIS) store data in different formats. One of the most common
format to store vector data is composed of 3 files (plus other optional ones):

   1. A shape file (.shp) that stores the geometry of the shapes (points, lines, polygons, etc). Each file can only
   store shapes of the same type, e.g. only points, only lines, etc. Moreover, the initial format only stored
   plane coordinates (x,y), but later modifications also include the z or elevation coordinate (e.g. PointsZ variant).
   
   2. A database file (.dbf) that stores information related to shapes in the .shp file. The information can be of
   different type: C (text), N or F (numeric), D (date), etc. The information for each shape is stored as a record
   that contains multiple fields of different type, e.g. record = (id: Text, pressure: Numeric, obs_date: Date, etc).
   QGis exports .dbf files in a dBase III format which is a standard format for small databases.
   
   3. An index file (.shx) that stores information about the location of the data in the 
   .dbf file, so it is possible to seek and retrieve information in random order without having to 
   parse the file from the beginning, hence avoiding extra computational cost.

For the purposes of a library such as PyGTV only the two first files are important, since
the main objective is to export the geometry and associated data without concern for optimization
of the process. Hence, early versions of PyGTV only include pure-Python parsers for the .shp and .dbf files, 
which are documented formats.

In addition to the 3 mandatory files, GIS software usually exports other files that
are important to interpret the data store in the .shp and/or .dbf files, for example
a projection file (.prj) that contains information about the geographical projection system
used to define the coordinates of the geometric shapes. PyGTV exports this information 
as comments in the VTK file.

A main obstacle to export shape files to VTK is that the later does not have an option
for text data associated to grid elements, e.g. cells or lines. Hence, text data
is not exported (TODO: check if it makes sense to export as comments).

 
