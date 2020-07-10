#!/bin/bash
displayNum=$1
time=2

killall -s 15 java

echo initializing directories

rm -rf /var/tmp/$displayNum
mkdir /var/tmp/$displayNum

sleep $time

echo creating display
Xvfb $displayNum -screen 0 1280x720x24+32 -fbdir /var/tmp/$displayNum &


sleep $time

echo starting desktop

export DISPLAY=$displayNum
exec startlxde &