#!/bin/bash

#
# Setup the repository
#

echo "Entered $0 ********************"
echo

# Install the public key for the repository (if not done previously):
curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add

# Create the repository configuration file:
sudo sh -c 'echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'

#
# Install pgAdmin
#

# Install for both desktop and web modes:
sudo apt install pgadmin4

# Install for desktop mode only:
#sudo apt install pgadmin4-desktop

# Install for web mode only:
sudo apt install pgadmin4-web

# Configure the webserver, if you installed pgadmin4-web:
sudo /usr/pgadmin4/bin/setup-web.sh


# 2/7/2021 =======================
# this has been removed, doesn't work with my installation anymore.
#sudo apt install pgadmin4 pgadmin4-apache2
#echo "ServerName 127.0.0.1" >> /etc/apache2/apache2.conf
#sudo systemctl status apache2
#sudo systemctl restart apache2

# http://127.0.0.1/pgadmin4/
# /usr/share/pgadmin4
# cd /etc/apache2/sites-available/
# vim pgadmin4.conf
# /etc/apache2/conf-enabled
#u: beheenmt@gmail.com  p: Bcsi7120@
