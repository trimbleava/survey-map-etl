#!/bin/bash

# Usage: ./dflow-workflow-std.sh tenant
# Description: This script assumes the code base is cloned into directory of your choice
#              as is. It then, installs the environment needed by the application such
#              database, redis cache, apache server, configurations and start the app.
# 
# Note: You could run this script from any directory as long as the path is specified.
#       Due to postgis/postgresql/gdal/ubuntu version dependencies, watch out if changing
#       the versions on any of these libraries in "set_env.sh" file

echo "Entered $0 Tenant: $1 ********************"
echo

#
# check the command line argiment
#
if [ "$1" = "" ]; then
    echo "Error: expected tenant's slug as the first argument."
    exit 1;
fi

#
# check system files availability
#
# envinronment must be sourced before running this script
CURDIR=`pwd`
export SCRDIR=$(dirname $(realpath $0))
export TENANT=$1

[[ ! -f $SCRDIR/set_env.sh ]] && { echo "Error: requires system file: '$SCRDIR/set_env.sh'" ; exit 1; }
source $SCRDIR/set_env.sh

#
# install and setup database postgres-12
#
echo "installing postgres database .........."
# bash $SCRDIR/install_postgres.sh    
echo

#
# installing postgis 3 database with extensions
#
echo "installing postgis database .........."
# bash $SCRDIR/install_postgis.sh     
echo

#
# install redis cache server
#
echo "installing redis cache server .........."
# bash $SCRDIR/install_redis.sh
echo

#
# setup project 
#
echo "setting up application ........."
# bash $SCRDIR/setup_project.sh
echo

#
# setup webserver
#
echo "setting up apache webserver .........."
bash $SCRDIR/deploy_apache.sh
echo
