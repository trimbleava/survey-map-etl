#!/bin/bash

# Usage: ./setup_project.sh
#

echo "Entered $0 ********************"
echo

# 
# setup django project
#
cd $PRJDIR
echo `pwd` "- current directory .........."

# clean if needed: ~/.cache/pip

PYV=`python3 --version`
PY_VER=${PYV:7:4}
VENV_STR="python"$PY_VER"-venv"

#
# create and activate venv - installs the pip in python3.8
#
echo "Creating new virtual environment for the project .........."
#
if [ $PY_VER == '3.8' ]; then
  [[ -d $PENV ]] || python3 -m venv "$PYENV"
elif [ $PY_VER == '3.7' ]; then
  [[ -d $PYENV ]] || sudo apt-get install -y python3.7-venv python3-pip && python3.7 -m venv $PYENV
elif [ $PY_VER == '3.6' ]; then
  [[ -d $PYENV ]] || sudo apt-get install -y python3.6-venv python3-pip && python3.6 -m venv $PYENV
else
  sudo apt-get install -y $VENV_STR python3-pip
  [[ -d $PYENV ]] || python$PY_VER -m venv $PYENV
  echo "Python version $PY_VER"
fi
echo

echo "Activating virtual env .........."
source "$PYENV/bin/activate"
echo $PYENV
echo

#
# install wheel
#
pip install wheel

#
# install gdal and geos system libraries to make sure they are complete for our project
#
echo "Installing gdal and geos  system libraries .........."
array=( gdal-bin libgdal-dev gdal-data libgdal-doc libgdal-perl libgeos++-dev libgeos-c1v5 libgeos-dev )
for i in "${array[@]}"
do
  TEST=`apt list --installed $i | grep installed` 
  [[ $TEST ]] || sudo apt-get -y install $i 
done
echo

echo "Installing python gdal binding libraries into venv .........."
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
# ogrinfo --version 
pip install GDAL==$(gdal-config --version | awk -F'[.]' '{print $1"."$2}')
echo

#
# install requirements 
#
echo "Installing project required libraries .........."
pip install -r $PRJDIR/requirements.txt
echo

#
# backup requirment with today's date
#
today=`date '+%Y_%m_%d'`           #_%H_%M_%S'`;
pip freeze > req_$today        

#
# write update/write wsgi.py file
#
echo "# Autogenerated WSGI config for $TENANT project." > $WSGIFILE
echo " " >> $WSGIFILE
echo " " >> $WSGIFILE
echo "import os,sys" >> $WSGIFILE
echo "import logging" >> $WSGIFILE
echo " " >> $WSGIFILE
echo " " >> $WSGIFILE
echo "logging.basicConfig(stream=sys.stderr)" >>  $WSGIFILE
echo " " >>  $WSGIFILE
echo "sys.path.insert(0, '$PRJDIR')" >>  $WSGIFILE
echo " " >>  $WSGIFILE
echo "sys.path.append('$PYENV/bin')" >>  $WSGIFILE
echo " " >>  $WSGIFILE
echo "sys.path.append('$PYENV/lib/python$PY_VER/site-packages')" >>  $WSGIFILE
# https://stackoverflow.com/questions/11505576/deploying-multiple-django-apps-on-apache-with-mod-wsgi/11515629#11515629
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'visual.setting_dir.prod_settings')
echo " " >>  $WSGIFILE
echo "os.environ['DJANGO_SETTINGS_MODULE'] = 'heath_lsa.setting_dir.prod_settings'" >> $WSGIFILE
# 
# TODO - same as above for asgi file, just change the module setting instead of rewriting
#

# WARNING:matplotlib:Matplotlib created a temporary config/cache directory at /tmp/matplotlib-c9ahx1p3 
# because the default path (/var/www/.config/matplotlib) is not a writable directory; it is highly recommended 
# to set the MPLCONFIGDIR environment variable to a writable directory, in particular to speed up the import of 
# Matplotlib and to better support multiprocessing.
echo "os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'" >> $WSGIFILE
echo " " >> $WSGIFILE
echo " " >> $WSGIFILE
echo "from django.core.wsgi import get_wsgi_application" >> $WSGIFILE
echo " " >> $WSGIFILE
echo "application = get_wsgi_application()" >> $WSGIFILE

chmod +x $WSGIFILE

#
# create secret key - secret.py in SCRDIR/, writes to SCRDIR/../secrets/secrete_key.txt
# need to delete if exists because we need to append to this file on the next statement.
# 
if [ -f $SECRETFILE ]; then
   rm $SECRETFILE
fi
python $SCRDIR/secret.py $SECRETFILE

#
# append more secretes, lines has order, see prod_settings
# these envs read from set_env. there is similar config in
# system.env that needs to be integrated.
echo "$DBNAME" >> "$SECRETFILE" 
echo "$DBUSER" >> "$SECRETFILE"  
# read pgpass get the password
PASS=`grep :$DBNAME $PGPASSFILE | cut -f5 -d:`
echo "$PASS" >> "$SECRETFILE"    
echo "$DBHOST" >> "$SECRETFILE"    
echo "$HOSTNAME" >> "$SECRETFILE"  

<<'comment'
#
# create superuser
#
# echo "Creating superuser for the project -- $DJANGO_SUPERUSER_USERNAME"
# with --database=$DBNAME only works from command line
python manage.py createsuperuser --noinput --noinput   # as of Django 3 or --no-input (reads all from DJANGO_SUPERUSER env, see set_env.sh)
# echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'pass')" | python manage.py shell

#
# python manage.py migrate  -- we already have a db dump, used the dump in install_postgis.sh
# 

#
# collect static
#
echo "Collecting statics .........."
python manage.py collectstatic --noinput
echo

#
# run the local server
#
echo "Running the application .........."
# python manage.py runserver &
comment


