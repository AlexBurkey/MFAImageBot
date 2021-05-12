#!/bin/bash

# Doing the work with the cron job to check every minute if the bot is running
python3 -u mfaimagebot.py prod >> "../logs/bot/$(date +"%FT%H%M%S").out" 
