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
# PyGTV is a small python library to read and export GIS information stored as shape (.shp)    #
# and associated (.dbf and .shx) files to VTK files that can be imported into visualization    #
# packages such as Paraview, VisIt or Mayavi.                                                  #
#                                                                                              #
# AUTHOR: Paulo Herrera R.                                                                     #
# DATE:   18/Mar/2019                                                                          #
################################################################################################

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-s", "--shape", dest="src",
                    help="path to shape file with or without extension .shp")
parser.add_argument("-d", "--dest", dest="dst",
                    help="path to VTK file without extension")
                    
parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                    help="print some information while reading files")

#parser.print_help()
args = parser.parse_args()

print("*"*40)
print("Exporting GIS data to VTK format...")
print("Shape file(s): " + args.src)
print("VTK output file: " + args.dst)
print("Verbose: " + str(args.verbose) )
print("-"*40)

###############################################################
#src = r"Dominio_modelo_SGA_modificado"
#src = "./gis/ex1/polygons.shp"
#dst = "./test_polygons"
###############################################################
import os
from Shape import CShape

src = args.src 
if "." in src:
    src = src.split(".")[0]
    
# DO SOME CHECKING FOR DST (EXIST?, CREATE?, ETC) 

shapes = CShape.readShapes(src, args.verbose)
CShape.toVTK(args.dst, shapes, args.verbose)

print("*** Done ***")
print("*"*40)
