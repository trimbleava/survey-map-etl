#!/bin/bash

echo "Entered $0 ********************"
echo


# Description: This file checks on all the application dependencies first, instead of running the scripts and in the middle 
#              of running, notice developer is missed a file!! 
#              Run this first first thing before running survey_map_workflow.sh
#
# Usage      : ./install_env.sh
#
# Developer  : Beheen Moghaddam-Trimble, 3/20/2021 - Eve of Persian's New Year
#	       Revisited on 3/13/2023
#
# TODO : Find all the commands we need to suppress sudo for, instead of ALL that is currently implemented!!
#        Username value, below? whoami = $USER = $LOGNAME 


#
# add the user to sudoer group
#
username=$LOGNAME
echo "Adding $username to sudoer group .........." 
# [: too many arguments -- one variable is split out into many arguments. double quote variable
# echo $(sudo -l -U beheen) 
TEST=$(sudo -l -U $username | grep "may run")
if [ ! "$TEST" ];  then
	sudo usermod -aG sudo $username
	sudo groups
fi
echo $TEST
echo
exit
#
# suppress the sudo password during the automation run. See /etc/sudoers format <%yourusername%	ALL=(ALL:ALL) ALL>
# where 1st ALL means: rule applies to this user, 2nd ALL means: rule applies to all hosts, 3rd:4th means this user
# can run commands on behalf of all_users:all_groups, fifth ALL means: all_commands or cmd1 cmd2 cmd3 cmd4 ...
# To manually add the NOPASSWD to the system file create a file with this command: "sudo visudo -f /etc/sudoers.d/a_file
# with no extension and not space in file name as shown below:
#         "beheen ALL=NOPASSWD: /usr/bin/apt-get /usr/bin/apt  or ALL instead of individual commands that is dangerous!
# any file you put on /etc/sudoers.d/ directory is being read by master file /etc/sudoers.
# 
# To do it progmatically, user runs all commands on behalf of all users and all groups. 
echo "Suppressing password prompt for sudoer .........."
echo
fname=$username"_nopass"
if [ ! -f /etc/sudoers.d/$fname ]; then
  text="$username ALL=(ALL) NOPASSWD: ALL"
  echo $text > $fname
  chmod 0440 $fname && sudo chown root:root $fname
  sudo mv $fname /etc/sudoers.d
fi
echo `ls -la /etc/sudoers.d/$fname`
echo

#
# send output/error into this empty log file - 
# we are redirecting apt commands from /var/log/apt/history.log to $LOG
#
<<'comment'
LOG=/opt/survey_map_apt.log
if [ ! -f $LOG ]; then
	> survey_map_apt.log 
	sudo mv dflow_std.log /opt 
fi
echo "Processing log file " `ls $LOG`
echo


# on Ubuntu is called dateutils - usage: dateutils.ddiff 2019-03-28 2019-05-16
echo "installing datautils .........."
sudo apt-get install dateutils  
echo
comment

#
# update and upgrade once at deploy time, recommended is 2 weeks
#
echo "Upgrading packages .........."
echo
sudo apt-get -y upgrade

<<'comment'
TEST=$(tac $LOG | grep -m1 -o "Upgrade") 

if [[ "$TEST" ]]; then
	# End-Date: 2021-02-09  18:52:38 backup: "End-Date: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}  [0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}" NOW=$(date +"%Y-%m-%d  %T")
	LAST_UPGRADE=$(tac $LOG | grep  -m1 -o "End-Date: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}" | cut -f2-3 -d" ")
	NOW=$(date +"%Y-%m-%d")
	diff=$(dateutils.ddiff "$LAST_UPGRADE" "$NOW")
    if [[ "$diff" > "15" ]]; then
    	sudo apt-get -y upgrade >> $LOG 2>&1
    	echo "Pakage repository last upgraded: $NOW"
    else
    	echo "Pakage repository last upgraded: $LAST_UPGRADE"
    fi
else
	sudo apt-get -y upgrade >> $LOG 2>&1     # first upgrade
	NOW=$(date +"%Y-%m-%d")
	echo "Pakage repository last upgraded: $NOW"
fi
comment
	 
echo


echo "Updating packages .........."
echo
sudo apt-get -y update

<<'comment'
TEST=$(tac $LOG | grep -m1 -o "Update") 

if [[ "$TEST" ]]; then
	# End-Date: 2021-02-09  18:52:38 backup: "End-Date: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}  [0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}" NOW=$(date +"%Y-%m-%d  %T")
	LAST_UPDATE=$(tac $LOG | grep  -m1 -o "End-Date: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}" | cut -f2-3 -d" ")
	NOW=$(date +"%Y-%m-%d")
	diff=$(dateutils.ddiff "$LAST_UPDATE" "$NOW")
    if [[ "$diff" > "15" ]]; then
    	sudo apt-get -y update >> $LOG 2>&1
    	echo "Pakage repository last updated: $NOW"
    else
    	echo "Pakage repository last updated: $LAST_UPGRADE"
    fi
else
	sudo apt-get -y upgrade >> $LOG 2>&1     # first update
	NOW=$(date +"%Y-%m-%d")
	echo "Pakage repository last updated: $NOW"
fi
comment
	 
echo

# add-apt-repository command is part of package software-properties-common 
# 
# install for git, lsb_release, netstat, curl
#
array=( git lsb-core net-tools curl wget software-properties-common)
for i in "${array[@]}"
do
	TEST=`apt-get list --installed $i | grep installed`
	[[ $TEST ]] || sudo apt-get -y install $i 
done
echo

<<'comment'
# for broken packages - apt is for the terminal while apt-get and apt-cache are for scripts
sudo apt-get update --fix-missing
sudo apt-get install -f
comment




