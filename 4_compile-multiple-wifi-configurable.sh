#!/bin/bash

if [ $# -ne 2 ]; then 
   echo "Usage: $0 config_file wifi_config_number"
   echo " "
   echo "Example: $0 foo.json 2"
   echo " "	   
   exit
fi

RANGE=$(jq -c '.Clients | length' $1)
SERVER_LWM2M=$(jq -r -c '.LWM2MServer' lwm2mconfig.json)
WIFI_SSID=$(jq -r -c '.WifiSSID'$2 lwm2mconfig.json)
WIFI_PWD=$(jq -r -c '.WifiPassword'$2 lwm2mconfig.json)
MAGIC_CODE=$(jq -r -c '.MagicCode' lwm2mconfig.json)
for ITER in `seq 1 $RANGE`
do
   ITMIN=$((ITER-1))
   TEST=$(jq -c '.Clients['$ITMIN']' $1)
   CLIENT=`jq -r -c '.Name' <(echo "$TEST")`
   PSKID=`jq -r -c '.PskId' <(echo "$TEST")`
   PSKPW=`jq -r -c '.PskPwd' <(echo "$TEST")`
   ISGPS=`jq -r -c '.Clients' gps_coords.json | jq '.[] | select(.Name=="'$CLIENT'")'`
   [ -z "$ISGPS" ] && continue
   GPS_LAT=`jq -r -c '.Clients' gps_coords.json | jq '.[] | select(.Name=="'$CLIENT'")' | jq -c -r '.Latitude'`
   GPS_LON=`jq -r -c '.Clients' gps_coords.json | jq '.[] | select(.Name=="'$CLIENT'")' | jq -c -r '.Longitude'`
   GPS_ALT=`jq -r -c '.Clients' gps_coords.json | jq '.[] | select(.Name=="'$CLIENT'")' | jq -c -r '.Altitude'`
   ./2_compile-single.sh "$CLIENT" "$SERVER_LWM2M" "$PSKID" "$PSKPW" "$WIFI_SSID" "$WIFI_PWD" "$GPS_LAT" "$GPS_LON" "$GPS_ALT" "$MAGIC_CODE" &> buildlog_$CLIENT.txt
   sleep 1
done
