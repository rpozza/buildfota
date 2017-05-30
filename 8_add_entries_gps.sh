#!/bin/bash

if [ $# -ne 4 ]; then 
   echo "Usage: $0 output_file name prefix_lat prefix_long"
   echo " "
   echo "Example: $0 foo.json egg 10.123 -30.234"
   echo " "	   
   exit
fi

NAME=$2
PRE_LAT=$3
PRE_LON=$4
FIRST_LOOP=true
echo "Type OUT to quit!"
printf '{\n' > $1
printf '   "Clients": [\n' >> $1 
while :
do
   read -p "Enter the Egg Number : " EGGN
   read -p "Enter GPS latitude   : " GPS_LAT
   read -p "Enter GPS longitude  : " GPS_LONG
   read -p "Enter GPS altitude   : " GPS_ALT
   if [ $EGGN == "OUT" ]
      then break
   fi
   if [ "$FIRST_LOOP" = false ] ; then
      printf ', \n' >> $1
   fi
   FIRST_LOOP=false
   printf '       { "Name":"%s%s", "Latitude":"%s%s", "Longitude":"%s%s", "Altitude":"%s" }' "$NAME" "$EGGN" "$PRE_LAT" "$GPS_LAT" "$PRE_LON" "$GPS_LONG" "$GPS_ALT">> $1 
done
printf '\n   ]\n}\n' >> $1
