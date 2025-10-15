#!/bin/bash
cd /app/telegram_bot
export $(cat .env | xargs)
pkill -f "python.*main.py" 2>/dev/null
sleep 2
service postgresql start 2>/dev/null
sleep 2
nohup python3 main.py > bot.log 2>&1 &
sleep 5
if ps aux | grep "python.*main.py" | grep -v grep > /dev/null; then
    echo "✅ Bot started successfully!"
    ps aux | grep "python.*main.py" | grep -v grep
else
    echo "❌ Bot failed to start. Check logs:"
    tail -20 bot.log
fi
