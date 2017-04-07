#!/bin/bash

if [ $# -ne 1 ]; then 
   echo "Usage: $0 build"
   echo " "
   echo "Example: $0 mybuild"
   echo " "	   
   exit
fi

cp $1 /media/rp0020/MBED$2/

