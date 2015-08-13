#!/bin/bash

# Script to launch Edax as an engine for othelloTk
#

# change this to Edax bin folder on your system
cd /home/john/dev/OthelloTk/edax/4.3.2/bin

# launch edax 
# use -n to set no. of processors
./lEdax-x64 -xboard -n 1

