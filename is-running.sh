#!/bin/bash
set -x #echo on

# print env
pwd
echo "~~~~~~"
date

if [[ $(ps -e | grep run.sh) ]]; then
    echo "Bot is running"
else
    echo "Bot is NOT running"
    echo "Restarting bot..."
    nohup ./run.sh &
fi