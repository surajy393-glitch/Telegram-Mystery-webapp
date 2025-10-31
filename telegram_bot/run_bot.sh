#!/bin/bash
# Script to keep the Telegram bot running

cd /app/telegram_bot

while true; do
    echo "$(date): Starting Telegram bot..."
    python3 -u main.py
    EXIT_CODE=$?
    echo "$(date): Bot stopped with exit code $EXIT_CODE"
    
    # If exit code is 0, bot was stopped intentionally, so exit
    if [ $EXIT_CODE -eq 0 ]; then
        echo "Bot stopped gracefully"
        exit 0
    fi
    
    # Otherwise, wait 5 seconds and restart
    echo "Restarting bot in 5 seconds..."
    sleep 5
done
