#!/bin/bash

INPUT=$1
OUTPUT=$2

arm-none-eabi-objcopy -I binary -O ihex ./$INPUT ./$OUTPUT

