#!/bin/bash
# Easy Bot Startup Script with Environment Variables

cd /app/telegram_bot

# Load environment variables
export $(cat .env | xargs)

# Kill any existing bot processes
pkill -f "python.*main.py" 2>/dev/null
sleep 2

# Start the bot in background
nohup python3 main.py > bot.log 2>&1 &

# Wait a bit for startup
sleep 3

# Check if bot is running
if ps aux | grep "python.*main.py" | grep -v grep > /dev/null; then
    echo "✅ Bot started successfully!"
    echo "📊 Bot process:"
    ps aux | grep "python.*main.py" | grep -v grep
    echo ""
    echo "📝 View logs with: tail -f /app/telegram_bot/bot.log"
    echo "🛑 Stop bot with: pkill -f 'python.*main.py'"
else
    echo "❌ Bot failed to start. Check logs:"
    tail -20 bot.log
fi
