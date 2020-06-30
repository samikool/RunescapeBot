#!/bin/bash
numBots=$1

for ((i=1; i<=$numBots; i++))
do
    export DISPLAY=:$i
    java -jar RuneLite.jar --mode=OFF &
done

