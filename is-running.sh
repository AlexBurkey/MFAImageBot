#!/bin/bash
set -x #echo on

# print env
echo "~~~~~~"
pwd
date


# TODO: Might also want to check if there are any python3 
# processes running.
# We could get multiple instances of bot processes running
if [[ $(pgrep run.sh) ]]; then
    echo "Bot is running"
else
    echo "Bot is NOT running"
    echo "Restarting bot..."
    # Sends output of run.sh to ./logs/monitor
    # info about when and how many times the bot has crashed
    #nohup ./run.sh >> "./logs/monitor/$(date +"%FT%H%M%S").out" &
fi