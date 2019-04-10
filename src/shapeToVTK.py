#! /usr/bin/env python

# ***********************************************************************************
# * Copyright 2019 Paulo A. Herrera. All rights reserved.                           *
# *                                                                                 *
# * Redistribution and use in source and binary forms, with or without              *
# * modification, are permitted provided that the following conditions are met:     *
# *                                                                                 *
# *  1. Redistributions of source code must retain the above copyright notice,      *
# *  this list of conditions and the following disclaimer.                          *
# *                                                                                 *
# *  2. Redistributions in binary form must reproduce the above copyright notice,   *
# *  this list of conditions and the following disclaimer in the documentation      *
# *  and/or other materials provided with the distribution.                         *
# *                                                                                 *
# * THIS SOFTWARE IS PROVIDED BY PAULO A. HERRERA ``AS IS'' AND ANY EXPRESS OR      *
# * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF    *
# * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO      *
# * EVENT SHALL <COPYRIGHT HOLDER> OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,        *
# * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,  *
# * BUT NOT LIMITED TO, PROCUREMEN OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,    *
# * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY           *
# * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING  *
# * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS              *
# * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                    *
# ***********************************************************************************

################################################################################################
# DESCRIPTION:                                                                                 #
#                                                                                              #
# Python Gis-to-Vtk (PyGTV) is a small python library to read and export GIS information       #
# stored as shape (.shp) and associated (.dbf and .shx) files to VTK files that can be         #
# imported into visualization packages such as Paraview, VisIt or Mayavi.                      #
#                                                                                              #
# AUTHOR: Paulo Herrera R.                                                                     #
# DATE:   18/Mar/2019                                                                          #
################################################################################################

def get_file_list(src, dst):
    """
    Check paths for source files (.shp) and destination (VTK files)
    :param src: it can be a file name with or without extension. It can be
                the .shp file or any other of the companying files (eg. .dbf)
                that share a common root.
                It can also be a directory with multiple .shp files. In this case,
                all files are exported to VTK format and saved to the dst directory.
    :param dst: path to the destination file without extension (if present, then it is removed)
                or to a directory. In the second case, the output file has the same root
                as the src file(s).
    """
    import os
    import glob
    assert os.path.exists(src)
    assert os.path.exists(dst)
    if os.path.isfile(dst): assert os.path.isfile(src), "Path to src must point to file"

    files_src, files_dst = [], []

    if os.path.isfile(src):
        if "." in src:
            src = src.split(".")[0]  # remove extension
        files_src.append(src)

    else: # directory
        g = os.path.join(src, "*.shp")
        ff = glob.glob(g)
        for f in ff:
            f = f.split(".")[0]      # remove extension
            files_src.append(f)

    if os.path.isfile(dst):
        if "." in dst:
            dst = dst.split(".")[0]  # remove extension
        files_dst.append(dst)
    else:
        for f in files_src:
            root = os.path.basename(f)
            if "." in root: root = root.split(".")
            fdst = os.path.join(dst, root)
            files_dst.append(fdst)

    assert len(files_src) == len(files_dst)

    return files_src, files_dst
    
#####################################
###### MAIN SCRIPT ##################
#####################################
from argparse import ArgumentParser
import os, sys
    
parser = ArgumentParser()
parser.add_argument("-s", "--shape", dest="src",
                    help="path to shape file with or without extension .shp")
parser.add_argument("-d", "--dest", dest="dst",
                    help="path to VTK file without extension or to directory where files should be saved")
parser.add_argument("-e", "--elev", dest="elev",
                    nargs='+', type=float, default=0.0,
                    help="default elevation for files that only have (x,y) coordinates")
parser.add_argument("-g", "--gui", dest="gui", action="store_true",
                    help="run simple graphical interface")
parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                    help="print some information while reading files")

if len(sys.argv) == 1: 
    sys.stderr.write("Missing arguments\n")
    parser.print_help(sys.stderr)
    sys.exit(1)
    
args = parser.parse_args()

###############################################################
#src = r"Dominio_modelo_SGA_modificado"
#src = "./gis/ex1/polygons.shp"
#dst = "./test_polygons"
###############################################################
import os
from gtv.files.shp import FileShp
from gtv.files.dbf import FileDbf
from gtv.files.prj import FilePrj
from gui import run_gui

if args.gui:
    run_gui(args)
    
else:
    print("*"*40)
    print("Exporting GIS data to VTK format...")
    print("Path to shape file(s): " + args.src)
    print("VTK output file: " + args.dst)
    print("Run gui: " + str(args.gui) )
    print("Verbose: " + str(args.verbose) )
    print("Default elevation: " + str(args.elev) )
    print("-"*40)

    # DO SOME CHECKING FOR DST (EXIST?, CREATE?, ETC)
    files_src, files_dst = get_file_list(args.src, args.dst)

    for i in range(len(files_src)):
        src, dst = files_src[i], files_dst[i]
        print("Processing files...")
        print("  src: %s"%files_src[i])
        print("  dst: %s"%files_dst[i])
        
        src_shp = src + ".shp"
        shp = FileShp.read(src_shp, verbose = False)         # pass the pointer to the file. It could be faster to read it at once into memory.
        print(shp)
        #shp.list_shapes()
        
        src_dbf = src + ".dbf"
        dbf = FileDbf.read(src_dbf)
        print(dbf)
        
        src_prj = src + ".prj"
        prj = FilePrj.read(src_prj)
        #print(prj)
        
        vals, text = dbf.get_records_as_lists()
        comments =            [".shp: " + shp.src]
        comments = comments + [".dbf: " + dbf.src]
        comments = comments + [".prj: " + prj.src]
        shp.toVTK(dst, vals, text, default_z = args.elev, verbose = args.verbose, comments = comments)
    
print("*** Done ***")
print("*"*40)
