#!/bin/bash

# Usage: 
# Note: Starting with February 1st 2019, GDAL master (released as GDAL 3.0) requires to be built and run against PROJ master (which will be released as PROJ 6.0)
#       See https://trac.osgeo.org/gdal/wiki/BuildingOnUnixGDAL25dev  AND https://trac.osgeo.org/gdal/wiki/rfc73_proj6_wkt2_srsbarn

echo "Entered build_geos_prj4_gdal.sh ...................."
echo



#
# build prj4
#

CURR_DIR=`pwd`
URL="http://download.osgeo.org/proj/proj-7.2.1.tar.gz"
PKG=${URL:(-17)}
DIR=${PKG:0:10}

source PRJLIB=`pwd`

echo "downloading $PKG .................... "
cd $PRJLIB

TEST="$PKG"
if [ -f "$TEST" ]; then
    echo "$PKG exists"
  else
    wget "$URL"
fi

TEST="$DIR"
if [ -d "$TEST" ]; then
    echo "$DIR exists"
  else
    tar xf "$PKG"
fi

echo
echo "builing .................... "
cd "$TEST"

make clean & make cleaninstall

./configure --prefix="$PRJLIB/libs" 
make 
make install

# With a successful install of PROJ we can now install data files using the projsync utility:
$PRJLIB/libs/bin/projsync --system-directory --endpoint https://cdn.proj.org --file us_noaa_README.txt   # just an example
# $PRJLIB/libs/bin/projsync --system-directory --all   # do this when needed, data goes to libs/share/proj

cd "$CURR_DIR"


#
# build geos-3.9.1
#

CURR_DIR=`pwd`
URL="http://download.osgeo.org/geos/geos-3.9.1.tar.bz2"
PKG=${URL:(-18)}
DIR=${PKG:0:10}

echo "downloading $PKG .................... "
cd $PRJLIB

TEST="$PKG"
if [ -f "$TEST" ]; then
    echo "$PKG exists"	  
  else
    wget "$URL"
fi

TEST="$DIR"
if [ -d "$TEST" ]; then
    echo "$DIR exists"
  else
    tar xf "$PKG"
fi

echo
echo "builing .................... "
cd "$TEST"

./autogen.sh

TEST="obj"
if [ -d "$TEST" ]; then
    rm -rf "$TEST"
  else
    mkdir "$TEST" && cd "$TEST"
fi

../configure --prefix="$PRJLIB/libs"
make  &&  make install
cd "$CURR_DIR"

#
# build gdal
#

CURR_DIR=`pwd`
URL="http://download.osgeo.org/gdal/3.2.1/gdal-3.2.1.tar.gz"
PKG=${URL:(-17)}
DIR=${PKG:0:10}

echo "downloading $PKG .................... "
cd $PRJLIB

TEST="$PKG"
if [ -f "$TEST" ]; then
    echo "$PKG exists"
  else
    wget "$URL"
fi

echo
echo "builing .................... "
TEST="$DIR"
if [ -d "$TEST" ]; then
    echo "$DIR exists"
  else
    tar xf "$PKG"
fi

cd $DIR

export LD_LIBRARY_PATH=$PRJLIB/libs/lib:$LD_LIBRARY_PATH
export PATH=$PRJLIB/bin:$PATH

CPPFLAGS=-I$PRJLIB/include LDFLAGS=-L$PRJLIB/lib ./configure  \
	 --with-python=/usr/bin/python3.8 \
	 --with-proj=$PRJLIB/libs \
         --with-geos=$PRJLIB/bin/geos-config \
	 --prefix=$PRJLIB/libs 

make -j4    # compile with 4 threads
make install

cd $CURR_DIR
echo $CURR_DIR " = " `pwd`

