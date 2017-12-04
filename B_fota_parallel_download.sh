#!/bin/bash

if [ $# -ne 4 ]; then
   echo "Usage: $0 range_start range_stop client_name number_of_parallel_downloads"
   echo " "
   echo "Example: $0 1 50 myclient 10"
   echo " "        
   exit
fi


NTHREADS=$4
NAME=$3
RANGE_IN=$1
RANGE_OUT=$2

for ITN in `seq -f "%03g" $RANGE_IN $RANGE_OUT`
do
   TEST=`ls $NAME$ITN*`
   [ -z "$TEST" ] && continue
   sem -j$NTHREADS "./6_fota_binary_downloader.py -c $NAME$ITN >& ./download_log_$ITN"
done
