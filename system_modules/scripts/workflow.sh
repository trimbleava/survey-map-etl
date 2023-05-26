#!/bin/bash

# steps to build, deploy, run this Django web application
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic

# database setup
sudo netstat -pnltu | grep "postgres"
ps aux | egrep --color apache2  or postgres
sudo systemctl start|stop|status apache2
# pgadmin4 is installed and setup during apache2 installation
/usr/pgadmin4/bin/setup-web.sh
http://127.0.0.1/pgadmin4/login?next=%2Fpgadmin4%2F