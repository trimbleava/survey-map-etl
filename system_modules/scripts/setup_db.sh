#!/bin/bash

# Usage: ./setup_db.sh
# Notes: make sure set_env.sh is sourced!
#        db must be running, to alter

echo "Entered $0 ********************"
echo 

#
# allow auth to connect with password, set above 
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
# restart and stat after config change, above
# if there is another version of a db is already running stop it.
#
sudo systemctl stop postgresql
sudo systemctl restart postgresql@$VER-main
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

# I think the -u using sudo unix password (set in sudoer.d) to login to postgres db 
# To test, remove the sudoer and then try this. In this case $PGPASSFILE is not picked up
sudo -u postgres psql postgres -c "ALTER USER postgres WITH password '$pass';"
echo
pass=   # reset for safety???
# psql -h $DBHOST -p $DBPORT -d postgres -U postgres  this types of connections picks up the $PGPASSFILE
 
#
# login as postgres db superuser to manage/delegate application database privileges
# using a sql file with necessary sql commands
#
# the environment variable, POSTDB, set in 'set_env.sh' file references a sql file
# with db commands to create the table space and application database
#
# psql automatic/nopassword login happens in this statement becasue of appropriate 
# authentication added to pg_hba.conf as well PGPASSWORD environment variable set.
# postgres user password must be set prior to use of $POSTDB
# 
psql -h $DBHOST -p $DBPORT -d postgres -U postgres -f $POSTDB
echo

