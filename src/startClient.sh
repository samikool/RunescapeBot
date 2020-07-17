#!/bin/bash
display=$1

export DISPLAY=$display
exec ./RuneLite.AppImage &
