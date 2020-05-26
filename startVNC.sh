#!/bin/bash
display=$1

exec x11vnc -geometry 1920x1080 -display :$display -ncache 10 -N -noipv6 -shared -nopw -onetile &