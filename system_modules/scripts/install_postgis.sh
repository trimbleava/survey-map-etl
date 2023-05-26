#!/bin/bash

# Usage: ./install_postgis.sh

echo "Entered $0 ...................."
echo


# Postgis compatibility matrix: https://trac.osgeo.org/postgis/wiki/UsersWikiPostgreSQLPostGIS

#
# check the key
#
KEY="ACCC 4CF8"
TEST=$(apt-key list 2> /dev/null | grep "$KEY")
if [[ ! $TEST ]]; then
    echo "adding key ...................."
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    echo
fi

# check the repo, if REPO line(s) is commented out won't work!
#
REPO="deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main"    
PGDG=/etc/apt/sources.list.d/pgdg.list
TEST=$(grep "$REPO" $PGDG)
if [[ ! $TEST ]]; then
    echo "adding repository ...................."
    echo "$REPO" | sudo tee -a "$PGDG" > /dev/null
    echo
fi
echo

# 
# install
#
echo "installing packages ...................."
sudo add-apt-repository ppa:ubuntugis/ppa -y
sudo apt-get -y install postgis postgresql-$VER-postgis-3
echo

#
# setting up postgis extension
#
echo "Setting up postgis extensions .........."
psql -h $DBHOST -p $DBPORT -d $DBNAME -U $DBUSER -f $POSTEXT
echo

#
# check the versions
#
echo "checking on database versions .........."
psql -h $DBHOST -p $DBPORT -d $DBNAME -U $DBUSER -c "SELECT version();"
psql -h $DBHOST -p $DBPORT -d $DBNAME -U $DBUSER  <<EOF
\x
SELECT PostGIS_Full_Version();
EOF
echo

<< 'comment'
postgis_full_version | POSTGIS="3.1.1 aaf4c79" [EXTENSION] PGSQL="120" GEOS="3.8.0-CAPI-1.13.1 " SFCGAL="1.3.7" PROJ="6.3.1" GDAL="GDAL 3.0.4, released 2020/01/28" LIBXML="2.9.10" LIBJSON="0.13.1" LIBPROTOBUF="1.3.3" WAGYU="0.5.0 (Internal)" TOPOLOGY RASTER
comment
#psql -h $DBHOST -p $DBPORT -d $DBNAME -U $DBUSER -c "SELECT PostGIS_Full_Version();"

#
# export the data into database, if exist TODO
#
echo "Populating database $DBNAME ........."
psql -h $DBHOST -p $DBPORT -d $DBNAME -U $DBUSER < $DBEXPORT
echo
