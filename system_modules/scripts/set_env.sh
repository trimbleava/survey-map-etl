#!/bin/bash

# Usage: source set_env.sh tenant
# Descr: first check the install_env.sh file, then this file. Make sure all the hardcoded
#        values are what you wanted to be. This should be the only place for  configuring 
#        this app. However, currently there are two files "postgis_extionssion.sql"   and
#        "post_db.sql" containing hard coded values. The first file is okay,  but the 2nd
#        file's hard coded values must be the same as those defined here.   I plan to fix
#        them ASAP.
#         

export DEV=1         # change this to 0 (must be int) to deploy into cloud, otherwise deploys into local

echo "Sourced set_env *******************"
echo 

echo "Setting environment for $TENANT debug level  $DEV .........."
#
# unset the variables, do not unset the SCRDIR
#
export PRJDIR=
export CONFDIR=
export PRJLIB=
export DBEXPORT=
export POSTDB=
export POSTEXT=
export PGPASSFILE=
export REQFILE=
export VER=
export PUBIP=
export PRJNAME=
export CONFDIR=
export PYENV=
export WSGIFILE=
export SECRETFILE=
export SRVADMIN=
export DOMAIN=
export STATDIR=
export MEDIADIR=
export DAEMON=
export WSGISSCRIPT=

#
# system path and application files - must exists!!
#
export PRJDIR="$(dirname $(dirname $(dirname $(realpath $0))))" # project directory, here is referring to system_modules 
export PRJLIB="$(dirname $(dirname $(dirname $(realpath $0))))" # location of libraries such as geos, prj4, gdal, NOT USED!
export POSTDB="$SCRDIR/post_db.sql"             # sql file containing database related stuff after postgres installation  
export POSTEXT=$SCRDIR"/postgis_extension.sql"  # sql file containing postgis related stuff after postgis installation
exportfile=$TENANT"_export.sql"
export DBEXPORT=$PRJDIR"/BACKUP/"$exportfile    # file name of the database dump
export PGPASSFILE="$SCRDIR/../secrets/pgpass.txt" # password secret file, read by psql if exists, chmod 0600 (either this of default ~/.pgpass)
export REQFILE="$PRJDIR/requirements.txt"    # python libraries required by application

[[ ! -f "$DBEXPORT"   ]] && { echo "Error: expected a $DBEXPORT file"; exit 1;   } 
[[ ! -f "$POSTDB"     ]] && { echo "Error: expected a $POSTDB file"; exit 1;     }
[[ ! -f "$POSTEXT"    ]] && { echo "Error: expected a $POSTEXT file"; exit 1;    }
[[ ! -f "$PGPASSFILE" ]] && { echo "Error: expected a $PGPASSFILE file"; exit 1; }
[[ ! -f "$REQFILE"    ]] && { echo "Error: expected a $REQFILE file"; exit 1;    }
[[ ! -f $SCRDIR/install_env.sh ]] && { echo "Error: requires system file: 'install_env.sh'" ; exit 1; }

# make sure permission on pgpass file is set correctly
chmod 0600 $PGPASSFILE

#
# system and application variables
#
OS=`lsb_release -r | grep "Release:" | cut -d ':' -f 2 | xargs`
echo $OS
echo
export VER=14                                   # version of postgresql to use, if needd pass it as variable
export POSTGRES_VER="postgresql-${VER}"         # postgres database to install and activate
export POSTGRES_USER=postgres                   # postgres supper user for the default postgres database
# export PGPASSWORD=postgre12                   # variable used by the psql client at runtime not safe on some OS - (use pgpass)

export POSTGRES_INITDB_ARGS=                    # postgres initialization arguments, if needed
export POSTGRES_HOST_AUTH_METHOD=md5            # changing default auth on postgres config file
export PGDATA="/etc/postgresql/${VER}/main"     # config location of postgreSQL database

export DBHOST=localhost                         # database host computer
export DBPORT=5432                              # database software is running on this port
export DBNAME=heath_lsa                         # application database name
export DBLOC="/opt/TENANT_DATA"                 # location of application data (repeated in post_db.sql!!)

export DJANGO_SUPERUSER_PASSWORD="heath_lsa_pass"        # as of Django 3, can createsuperuser from this env
export DJANGO_SUPERUSER_USERNAME="heath_lsa_admin"       # as of Django 3, can createsuperuser from this env 
export DJANGO_SUPERUSER_EMAIL="Ava.Trimble@heathus.com"
export DBUSER=$DJANGO_SUPERUSER_USERNAME        # application superuser, same as SUPERUSER

#
# webserver variables
#
if [ ! $DEV ]; then 
export PUBIP=$(curl -4 icanhazip.com)           # google cloud compute engine external ip (i.e. 35.193.244.81)
else
export PUBIP=127.0.1.1                          # local host
fi;
export HOSTNAME=$PUBIP                          # host name used in setting to connect to webserver host name
#

export TENANT=$TENANT                            # tenant slug used in webserver naming
export PRJNAME=$TENANT                          # project name used in webserver naming -- remove this
export CONFDIR="$SCRDIR/../system_configs"      # project codebase configuration location, holds cofig files
export SRVADMIN="Ava.Trimble@heathus.com"       # any server error/message gotes to this email
export DOMAIN="lsa.etl.heatus.com"              # if regiter domain (visual.com = 35.193.244.81, add A record for both visual.com 
                                                # and www.visual.com for this to work in real deployment DNS)
export STATDIR="$PRJDIR/static"                 # location of django collectstatic - must be same as location in application
export MEDIADIR="$PRJDIR/media"                 # location of uploads - must be same as location in application
export DAEMON="apache2"                         # on some os this is httpd
export WSGISSCRIPT="$PRJDIR/heath_lsa"          # location of wsgi.py file of application in the django project
export PYENV="$PRJDIR/../PY_ENV"                # project virtual env name
export WSGIFILE="$WSGISSCRIPT/wsgi.py"          # wsgi script is created dynamically
export SECRETFILE="$SCRDIR/../secrets/secret_key.txt"      # secret file is created dynamically - has a dependency in prod_settings.py

echo 'Environment set ...................'
echo 'PROJECT DIR   :' $PRJDIR
echo 'SCRIPTS DIR   :' $SCRDIR
echo 'POSTGRES VER  :' $POSTGRES_VER
echo 'PGD CONF LOC  :' $PGDATA
echo 'PGPASSFILE    :' $PGPASSFILE
echo 'DBHOST        :' $DBHOST 
echo 'DBPORT        :' $DBPORT
echo 'DBUSER        :' $DBUSER
echo 'DBNAME        :' $DBNAME
echo 'POSTDB        :' $POSTDB
echo 'POSTEXT       :' $POSTEXT
echo 'DBEXPORT      :' $DBEXPORT
echo 'PRJLIB        :' $PRJLIB
echo 'PUBIP         :' $PUBIP
echo 'PYENV         :' $PYENV
echo 'CONFDIR       :' $CONFDIR
echo 'PRJNAME       :' $PRJNAME
echo 'DOMAIN        :' $DOMAIN
echo 'SRVADMIN      :' $SRVADMIN
echo 'STATDIR       :' $STATDIR
echo 'MEDIADIR      :' $MEDIADIR
echo 'DAEMON        :' $DAEMON
echo 'WSGISSCRIPT   :' $WSGISSCRIPT
echo
