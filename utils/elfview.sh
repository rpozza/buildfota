#!/bin/bash

INPUT=$1
readelf -a ./$INPUT | less
