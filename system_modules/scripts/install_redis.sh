#!/bin/bash

# Usage: ./install_redis.sh


echo "Entered $0 ********************"
echo

#
# install redis if it is not installed
#
TEST=`apt-cache policy "redis-server" | grep "Installed: (none)"`

if [[ $TEST ]]
  then 
    echo "installing redis server ...................."
    sudo apt-get -y install redis-server redis-tools  
  else  
    echo "redis-server is already installed ...................."
    echo  
fi

#
# stop redis-server if it is running
#
TEST=`systemctl status redis-server | grep "(running)"`
[[ $TEST ]] && sudo systemctl stop redis-server || echo "redis-server is not running - OK"
echo
   
#   
# init server: manage as a service, set password, memory, THP 
#
sudo sed -i -e 's/supervised no/supervised systemd/' /etc/redis/redis.conf
sudo sed -i -e 's/# unixsocket/unixsocket/' /etc/redis/redis.conf
sudo sed -i -e 's/# unixsocketperm/unixsocketperm/' /etc/redis/redis.conf
# Note that Redis will write a pid file in /var/run/redis.pid when daemonized.
sudo sed -i -e 's/daemonize no/daemonize yes/' /etc/redis/redis.conf
echo

<< 'comment'
PASS=`openssl rand 60 | openssl base64 -A`
# to pass variable use double qoute and use different seperator like bar | if your variable contains "/" 
sudo sed -i "s|# requirepass foobared|requirepass $PASS|g" /etc/redis/redis.conf

# 24864:M 16 Feb 08:22:57.815 # Server initialized
# 24864:M 16 Feb 08:22:57.815 # WARNING overcommit_memory is set to 0! Background save may fail under low memory condition. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
STR="vm.overcommit_memory = 0"
FLE="/etc/redis/redis.conf"
TEST=$(sudo grep "$STR" $FLE)
echo "$TEST"
if [[ ! $TEST ]]; then
    echo "$STR" | sudo tee -a "$FLE" > /dev/null
fi
#sudo sh -c 'echo "vm.overcommit_memory = 0" >> /etc/redis/redis.conf'

# 24864:M 16 Feb 08:22:57.815 # WARNING you have Transparent Huge Pages (THP) support enabled in your kernel. This will create latency and memory usage issues with Redis. To fix this issue run the command 'echo never > /sys/kernel/mm/transparent_hugepage/enabled' as root, and add it to your /etc/rc.local in order to retain the setting after a reboot. Redis must be restarted after THP is disabled.
# sudo sh -c 'echo "never > /sys/kernel/mm/transparent_hugepage/enabled" >> /etc/rc.local'    TODO

comment


# if redis-server.service file is missed in directory path /etc/systemd/system/
# so we have to create file into this directory using command like:
TEST="/etc/systemd/system/redis-server.service"
if [[ -L $TEST ]]; then
    echo "$TEST exists"
    echo
else
    sudo ln -s /lib/systemd/system/redis-server.service /etc/systemd/system/redis-server.service
    echo
fi

# start the server
sudo systemctl start redis-server     # Beheen 3/14/23 - this gives error!! /etc/redis/redis.conf --no-pager
echo

<<'comment'
# test redis functionality
sudo systemctl status redis-server.service           # Beheen does respond with '.service'
echo
sudo netstat -lnp | grep redis-server                # Beheen doesn't respond with '.service'
echo
ls /var/run/redis/redis-server.pid
echo
comment
