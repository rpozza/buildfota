#!/bin/bash

if [ $# -ne 3 ]; then 
   echo "Usage: $0 config_file server_ip server_port"
   echo " "
   echo "Example: $0 myconf.json 192.168.0.1 80"
   echo " "	   
   exit
fi

RANGE=($(jq -c '.Clients | length' $1))
for ITER in `seq 1 $RANGE`
do
   ITMIN=$((ITER-1))
   TEST=($(jq -c '.Clients['$ITMIN']' $1))
   CLIENT=`jq -r -c '.Name' <(echo "$TEST")`
   PSKID=`jq -r -c '.PskId' <(echo "$TEST")`
   PSKPW=`jq -r -c '.PskPwd' <(echo "$TEST")`
   curl -X PUT -d '{ "endpoint" : "'$CLIENT'", "psk": { "identity": "'$PSKID'", "key": "'$PSKPW'" } }' http://$2:$3/api/security/clients
done
