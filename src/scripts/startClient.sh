#!/bin/bash
display=$1

export DISPLAY=$display

./RuneLite.AppImage >/dev/null 2>&1 &
clientPID=$!
#sleep 1

if ps | grep " $clientPID " 
then
    echo "clientPID=${clientPID}"
    exit 0
else 
    exit 1
fi