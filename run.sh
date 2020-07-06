#!/bin/bash

FAILS=0

while true
do
  python3 -u bot.py prod # your program
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
