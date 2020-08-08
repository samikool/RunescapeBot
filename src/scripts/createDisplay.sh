#!/bin/bash
displayNum=$1

#this command should be able to detect if a display exists or not
## xdpyinfo -display :1 | grep unable 

rm -rf /var/tmp/$displayNum
mkdir /var/tmp/$displayNum

Xvfb $displayNum -screen 0 1280x720x24+32 -fbdir /var/tmp/$displayNum 2>&1 &
dispPID=$!

if ps | grep " $dispPID " 
then
    export DISPLAY=$displayNum
    startlxde >/dev/null 2>&1 &
    deskPID=$!
    echo "dispPID=${dispPID}"
    echo "deskPID=${deskPID}"
    exit 0
else 
    exit 1
fi