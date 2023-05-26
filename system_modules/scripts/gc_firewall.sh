#!/bin/bash

#
# check/create/delete firewall rule
#
cmd='$1'         # create, delete, list
name='$2'
protocol='$3'    # The Secure Shell (SSH) Connection Protocol, tcp, udp, icmp, esp, ah, sctp, or any IP protocol number
port='$4'
direction='$5'   # INGRESS, EGRESS, IN, OUT

network='$6'     # A Virtual Private Cloud (VPC) network is a virtual version of a physical network, implemented inside of Google's production network, 
                 # using Andromeda. Projects can contain multiple VPC networks. Unless you create an organizational policy that prohibits it, new projects 
                 # start with a default network (an auto mode VPC network) that has one subnetwork (subnet) in each region. gcloud compute networks list
                 
action='$7'      # ALLOW, DENY, if action --rule must be specified, there is a difference between --rule and --allow
rule='$8'        # --rules=PROTOCOL[:PORT[-PORT]],[…]

if [ -z "$1" ]; then
    echo -e "\nSetting command to 'check'\n"
    cmd='list'
fi
if [ -z "$2" ]; then
    echo -e "\nSetting rule name to 'default'\n"
    name='default'
fi
networks=$(gcloud compute networks list)
#gcloud compute firewall-rules $cmd --project $project -q  $name --allow $protocol:$port --direction $dir --network $network
#default	
#us-east1
#10.142.0.0/20
#10.142.0.1
#Off
#Off
project=$(gcloud config list --format='text(core.project)')
echo $project
