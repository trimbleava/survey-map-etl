#!/bin/bash

# Usage: ./deploy_apache.sh
# Desc : This script is running from an AZURE VM instance of type Ubuntu20.4.
# Notes: a) we want to deploy our django project codebase that we git cloned into 
#           $USER on the VM. 
#        b) you could run this script from any directory as long as the path is specified.
#       

echo "Entered $0 ********************"
echo

#
# pre-conditons - TODO
# at this time all the codebased have been copied to $PRJDIR
# workflow script is executed
# using set_env variables in this file too.
#

#
# check firewall/create rules - TODO
# for http,https,tcp,

<<'comment'
#
# install apache2
#
sudo apt-get -y install apache2 apache2-dev

#
# install wsgi adapter for apache
#
# see location of installed adapter in Debian buster:
# /etc/apache2/mods-available/wsgi.load
# /etc/apache2/mods-available/wsgi.conf
# /usr/lib/apache2/modules/mode_wsgi.so
#

sudo apt-get -y install libapache2-mod-wsgi
sudo apt-get -y install libapache2-mod-wsgi-py3
# check for dependencies if they are installed 
# apache2-dev debhelper dh-autoreconf python-all-dev python3-all-dev -- dependencies
# enable adapter
sudo a2enmod wsgi.load 
comment

#
# create the apache config file per tenant - TODO: remove PRJNAME for TENANT
# 

echo "Writing to config directory: $CONFDIR/$TENANT.conf .........."
echo
#
# create a new file
#
touch $CONFDIR/$TENANT.conf

# 
# write to new file
#
CONFILE=$CONFDIR/$TENANT".conf"
# Defines the directory and name prefix to be used for the UNIX domain sockets used by 
# mod_wsgi to communicate between the Apache child processes and the daemon processes.
# srwx------  1 www-data          root        0 Apr  7 09:43 .85546.0.2.sock
# srwx------  1 www-data          root        0 Apr  7 09:43 dflow_wsgi.85546.0.1.sock
# ldd /usr/lib/apache2/modules/mod_wsgi.so -- mod_wsgi.so must be compiled with the same python in use
SOCK=$TENANT"_wsgi"
# installed apache2-dev to run:  apxs -q runtimedir
# this shows where apache2 socket is running and run from there.
# I am not running it in the same place though.
echo "WSGISocketPrefix /var/run/$SOCK" > $CONFILE      
echo "<Directory $PRJDIR>" >> $CONFILE
echo "    Require all granted" >> $CONFILE
echo "</Directory>" >> $CONFILE
echo "<VirtualHost *:80>" >> $CONFILE
echo "     DocumentRoot \"$PRJDIR\"" >> $CONFILE
echo "     ServerAdmin $SRVADMIN" >> $CONFILE
echo "     ServerName $PUBIP" >> $CONFILE                      
echo " "  >> $CONFILE
echo "     ServerAlias $DOMAIN" >> $CONFILE                     
echo "     Alias /robots.txt  $STATDIR/robots.txt" >> $CONFILE
echo "     Alias /favicon.ico $STATDIR/img/favicon.ico" >> $CONFILE
echo "     Alias /static/ $STATDIR" >> $CONFILE
echo "     Alias /media/ $MEDIADIR" >> $CONFILE
ERROR="_error.log"
ACCESS="_access.log"
echo "     ErrorLog  \"/var/log/$DAEMON/$PRJNAME$ERROR\"" >> $CONFILE
echo "     CustomLog \"/var/log/$DAEMON/$PRJNAME$ACCESS\"" combined >> $CONFILE
echo "     <Directory $PRJDIR>" >> $CONFILE
echo "        Options +Indexes" >> $CONFILE
echo "        Order allow,deny" >> $CONFILE
echo "        Allow from all" >> $CONFILE
echo "     </Directory>" >> $CONFILE
echo "     # Serving static files from this directory" >> $CONFILE
echo "     <Directory $STATDIR>" >> $CONFILE
echo "        Options -Indexes" >> $CONFILE
echo "        Order deny,allow" >> $CONFILE
echo "        Require all granted" >> $CONFILE
echo "     </Directory>" >> $CONFILE
echo "     # Serving media files from this directory" >> $CONFILE
echo "     <Directory $MEDIADIR>" >> $CONFILE
echo "        Options -Indexes" >> $CONFILE
echo "        Order deny,allow" >> $CONFILE
echo "        Require all granted" >> $CONFILE
echo "     </Directory>" >> $CONFILE

echo "     WSGIDaemonProcess $PRJNAME processes=2 threads=15 display-name=%{GROP} python-path=$PYENV:$PRJDIR" >> $CONFILE
echo "     WSGIProcessGroup $PRJNAME" >> $CONFILE
echo "     WSGIApplicationGroup %{GLOBAL}" >> $CONFILE

echo "     <Directory $PYENV>" >> $CONFILE
echo "        AllowOverride None" >> $CONFILE
echo "        Options None" >> $CONFILE
echo "        Require all granted" >> $CONFILE
echo "     </Directory>" >> $CONFILE
echo "     WSGIScriptAlias / $WSGISSCRIPT/wsgi.py" >> $CONFILE
echo "     <Directory $WSGISSCRIPT>" >> $CONFILE
echo "        Order allow,deny" >> $CONFILE
echo "        Allow from all" >> $CONFILE
echo "     </Directory>" >> $CONFILE
echo " </VirtualHost>" >> $CONFILE

#
# copy your_domain.conf into apache webserver predefined location
#
sudo cp $CONFILE /etc/apache2/sites-available

#
# appropraite the site directory
#
if [ -d $PRJDIR ]; then 
    # sudo mkdir -p /var/www/$PRJNAME;
    # most likely it is under user name already
    sudo chown -R $USER:$USER $PRJDIR;
    # make sure the permission is set correclty
    sudo chmod -R 755 $PRJDIR;
else
    echo "Project directory and files do not exist!!, how this happend???"
    exit
fi;

#
# activate webserver - not need to be in apache dir to enable/disable
#
sudo a2ensite $TENANT.conf           # enable our new site
sudo a2dissite 000-default.conf      # disable the default site
sudo apache2ctl configtest           # test new configuration file
# sudo systemctl reload $DAEMON        # if config changes
sudo systemctl restart $DAEMON       # restart apache to implement the new changes
# check the log files in:
# /var/log/apache2/access.log and /var/log/apache2/error.log
# /var/log/$DAEMON/$PRJNAME$ERROR
# /var/log/$DAEMON/$PRJNAME$ACCESS
echo "to check apache: http://localhost:80"
echo

