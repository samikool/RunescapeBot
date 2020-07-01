#!/bin/bash
numBots=$1
time=5

killall -s 15 Xvfb
killall -s 15 java

echo initializing directories
for ((i=1; i<=$numBots; i++))
do
    rm -rf /var/tmp/$i
    mkdir /var/tmp/$i
done

sleep $time

echo creating displays
for ((i=1; i<=$numBots; i++))
do
    Xvfb :$i -screen 0 1920x1080x24+32 -fbdir /var/tmp/$i &
done

sleep $time

echo starting desktops
for ((i=1; i<=$numBots; i++))
do
    export DISPLAY=:$i
    exec startlxde &
done

#sleep $time    

# echo starting VNC servers
# for ((i=1; i<=$numBots; i++))
# do
#     #Start VNC Server
#     
# done

