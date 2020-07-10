#!/bin/bash

FAILS=0

while true
do
  # your program
  # Sends output to ./logs/bot file
  python3 -u bot.py >> "./logs/bot/$(date +"%FT%H%M%S").out" 
  EXIT=$?
  ((FAILS++))

  if [[ $FAILS -gt 50 ]]
  then
    echo "[$(date)] failed to many times. aborting ..."
    exit 1
  fi

  echo "[$(date)] bot exited with code $EXIT."
  echo "Current number of failures: $FAILS"
  echo "Restarting ..."
  sleep 0.5m

done
