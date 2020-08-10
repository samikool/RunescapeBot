#!/bin/bash
display=$1

#-onetile
#-geometry 1920x1080
#-ncache 10
#-once -- only allow one connection opposite of -forever

export DISPLAY=$display
x11vnc -display $display -N -noipv6 -shared -nopw -quiet -forever 2>&1 &
vncPID=$!
#sleep 1

if ps | grep " $vncPID "
then
    echo "vncPID=${vncPID}"
    exit 0
else
    exit 1
fi