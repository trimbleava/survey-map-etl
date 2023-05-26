#!/bin/bash

# Usage: ./dflow-std-clean.sh
# Descr: unistall the application to start as a clean slate.  
# Note: you could run this script from any directory as long as the path is specified.


echo "Entered $0 ********************"
echo

#
# check system files availability
#
# env must be sourced before running this script
CURDIR=`pwd`
_SRCDIR=$(dirname $(realpath $0))

[[ ! -f $_SRCDIR/set_env.sh ]] && { echo "Error: requires system file: '$_SRCDIR/set_env.sh'" ; exit 1; }
source $_SRCDIR/set_env.sh 
echo

#
# uninstall postgres, redis, postgis
#
sudo systemctl stop postgresql
sudo systemctl stop redis-server
echo

sudo apt-get -y purge postgresql-$VER postgresql-client-$VER
echo  
sudo apt-get -y purge redis-server redis-tools   
echo
sudo apt-get -y purge postgis postgresql-$VER-postgis-3
echo

#
# remove databases, venv
#
sudo rm -rf /opt/CCI_DATA
echo
sudo rm -rf $PRJDIR/$PYENV
echo
#
# remove latest geos,proj4, gdal
#
sudo apt-get -y remove gdal-bin libgdal-dev gdal-data libgdal-doc libgdal-perl libgeos++-dev libgeos-c1v5 libgeos-dev

#
# remove webserver stuff
#
# disable adapter - not need to be in apache dir to enable/disable
sudo a2dismod wsgi.load SS
# disable site config
sudo a2dissite $PRJNAME.conf
# remove the site config file
sudo rm /etc/apache2/sites-available/$PRJNAME.conf 
echo    
#
# uninstall apache and wsgi adapters
sudo apt-get -y remove apache2
sudo apt-get -y remove libapache2-mod-wsgi
sudo apt-get -y remove libapache2-mod-wsgi-py3
# check for dependencies if they are removed
# apache2-dev debhelper dh-autoreconf python-all-dev python3-all-dev -- dependencies
#
echo
#
# remove the local codebase config 
# 
CONFILE="$CONFDIR/$PRJNAME.conf"
sudo rm $CONFILE
echo
#
# remove wsgi and secret file
#
sudo rm $WSGIFILE
sudo rm $SECRETFILE
echo 



