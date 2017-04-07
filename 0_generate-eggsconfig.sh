#!/bin/bash

if [ $# -ne 4 ]; then 
   echo "Usage: $0 output_file range_start range_stop client_name"
   echo " "
   echo "Example: $0 foo.json 1 2 mylwm2mclient"
   echo " "	   
   exit
fi

NAME=$4
RANGE_IN=$2
RANGE_OUT=$3

printf '{\n' > $1
printf '   "Clients": [\n' >> $1 
for EGGN in `seq -f "%03g" $RANGE_IN $RANGE_OUT`
do
   PSK_ID=`openssl rand -hex 5`
   PSK_PWD=`openssl rand -hex 16`
   printf '       { "Name":"%s%s", "PskId":"%s", "PskPwd":"%s" }' "$NAME" "$EGGN" "$PSK_ID" "$PSK_PWD" >> $1 
   if [ $EGGN == `printf "%03g" $RANGE_OUT` ]
      then break
   fi 
   printf ', \n' >> $1
done
printf '\n   ]\n}\n' >> $1
