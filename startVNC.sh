#!/bin/bash
display=$1

#-onetile
#-geometry 1920x1080
#-ncache 10
#-once -- only allow one connection opposite of -forever


exec x11vnc -display :$display -N -noipv6 -shared -nopw &