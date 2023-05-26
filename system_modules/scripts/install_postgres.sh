#!/bin/bash

# This script stops the running database, if any and installs a version of postgresql 
# database where the version is configured as an environment variable, see set_env.sh
#
# The steps taken during installation are:
# 1) add the authentication key to trusted app, if it doesn't exist
# 2) add the repository site to download the app from, if it doesn't exist
# 3) stop an existing and running postgreSQL server regardless of version
# 4) install the defined version postgresql with dependencies
# 5) run at boot 
###and start running the version server and show the status
# 6) show status of the psql client version. 
#
# Note that with ubuntu18.04 and up postgreSQL 13 is installed and psql client 
#    version 13.0 is active. I could not find how to use psql client version 12 
#    after installing postgreSql version 12.0. I left this default version for now.
#
# /usr/lib/postgresql/14/bin/postgres
# the data directory where all the database clusters will be stored at:
# /var/lib/postgresql/14/main
# and the configuration file at:
# /etc/postgresql/14/main/postgresql.conf 
#
echo "Entered $0 ********************"
echo

# 
# 1 - check the key
# 
KEY="ACCC 4CF8"
TEST=$(apt-key list 2> /dev/null | grep "$KEY")
if [[ ! $TEST ]]; then
    echo "adding key ...................."    
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    echo
fi

#
# 2 - check the repo, if REPO line(s) is commented out won't work!
#
REPO="deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main"
PGDG=/etc/apt/sources.list.d/pgdg.list
TEST=$(grep "$REPO" $PGDG)
if [[ ! $TEST ]]; then
    echo "adding repository ...................."    
    # sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
    echo "$REPO" | sudo tee -a "$PGDG" > /dev/null
    echo
fi


# 
# 3 - stop the running version of postgresql
#     Note: the running version is using default port 5432. So watch out. 
#  
sudo systemctl stop postgresql
sudo systemctl unmask postgresql   # better safe than sorry - has happend
echo

# installed pakages are referenced in apt-cache, when extracted gives lines like: 
# postgresql-12:
# Installed: (none)
# OR
# postgresql-12:
# Installed: 12.6-1.pgdg18.04+1
#
TEST=`apt-cache policy "$POSTGRES_VER" | grep "Installed: (none)"`

if [[ $TEST ]]
  then 
    echo "installing $POSTGRES_VER ...................."
   
    # 4 - install this version
    sudo apt-get -y install $POSTGRES_VER postgresql-contrib postgresql-common postgresql-client-common postgresql-client-$VER
    echo
    # 5 - run at boot
    sudo systemctl enable postgresql@$VER-main.service
    
    
  else  
    echo "$POSTGRES_VER is already installed ...................."
    echo
    
fi

#
# allow auth to connect with password
#
CONF="host    all             all             all                     md5"
PGHBA="$PGDATA/pg_hba.conf"
TEST=$(sudo grep "$CONF" $PGHBA)
if [[ ! $TEST ]]; then
    echo "authenticating ...................."
    echo "$CONF" | sudo tee -a "$PGHBA" > /dev/null
    #echo "host    all             all             all                     md5" | sudo tee -a "$PGDATA/pg_hba.conf" > /dev/null
    echo
fi

# changing the port to default 5432
echo "checking the port number ...................."
sudo sed -i "/^port/c\port = $DBPORT                             # (change requires restart)" $PGDATA/postgresql.conf
echo

#
# start after config changes above
# if there is another version of a db is already 
# running stop it, although this should not happen
#
sudo systemctl stop postgresql
sudo systemctl start postgresql@$VER-main
# sudo netstat -pnltu | grep "postgres"
# sudo systemctl status postgresql@$VER-main
echo

#
# setup for application database
#
echo "setting up application database ...................."
#
# created application data directory outside database software to be independent 
# of the db vesion. this directory must be owned by postgres with 700 permission.
# check on user database directory, create if it doesn't exists. Must be empty dir.
# 
if [ ! -d "$DBLOC" ]
then
    sudo mkdir -p -v -Z $DBLOC && sudo chown postgres:postgres "$DBLOC" && sudo chmod 700 "$DBLOC"  
    echo "created application database $DBLOC."
else
    echo "application database $DBNAME exists"
fi
echo

#
# set postgresql password - use the pass in pgpassfile (hostname:port:database:username:password)
#
pass=`grep :postgres $PGPASSFILE | cut -f5 -d:`
sudo -u postgres psql postgres -c "ALTER USER postgres WITH password '$pass';"
echo
pass=   # reset for safety???
# psql -h $DBHOST -p $DBPORT -d postgres -U postgres  this types of connections picks up the $PGPASSFILE
 
#
# login as postgres db superuser to manage/delegate application database privileges
# using a sql file with necessary sql commands. The environment variable, POSTDB, 
# set in 'set_env.sh' file references a sql file with db commands to create the table 
# space and application database
#
# psql automatic/nopassword login happens in this statement becasue of appropriate 
# authentication added to pg_hba.conf as well PGPASSWORD environment variable set.
# postgres user password must be set prior to use of $POSTDB
# 
# create role, tablespace and db
#
psql -h $DBHOST -p $DBPORT -d postgres -U postgres -f $POSTDB
echo

<<'comment'
# check the status of this version
sudo systemctl status postgresql@$VER-main.service 
# show psql version
sudo psql --version
echo
comment
