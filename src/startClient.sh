#!/bin/bash
display=$1

export DISPLAY=$display
java -jar RuneLite.jar --mode=OFF &