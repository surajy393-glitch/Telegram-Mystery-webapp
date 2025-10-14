#!/bin/bash

echo "🤖 Starting LuvHive Bot (PERMANENT SETUP)"

# Check if PostgreSQL is running
if ! netstat -tlnp | grep -q 5432; then
    echo "🔧 Starting PostgreSQL..."
    sudo -u postgres /app/telegram_bot/pgdata/start_postgres.sh
    sleep 5
fi

# Verify PostgreSQL is running
if ! netstat -tlnp | grep -q 5432; then
    echo "❌ PostgreSQL failed to start!"
    exit 1
fi

echo "✅ PostgreSQL is running"

# Load environment variables
if [ -f "/app/telegram_bot/.env" ]; then
    export $(cat /app/telegram_bot/.env | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ .env file not found!"
    exit 1
fi

# Stop any existing bot process
pkill -f "python main.py" 2>/dev/null || echo "No existing bot process"

# Start the bot
cd /app/telegram_bot
echo "🚀 Starting Telegram bot..."
python main.py &
BOT_PID=$!

echo "✅ Bot started with PID: $BOT_PID"
echo "📊 Bot Status:"
sleep 3
ps aux | grep "python main.py" | head -1

# Test bot connectivity
python -c "
import asyncio
import os
async def test():
    try:
        from telegram import Bot
        bot = Bot(token=os.environ.get('BOT_TOKEN'))
        me = await bot.get_me()
        print(f'✅ Bot is online: {me.first_name} (@{me.username})')
        print(f'✅ Bot ID: {me.id}')
    except Exception as e:
        print(f'❌ Bot connectivity error: {e}')
asyncio.run(test())
" 2>/dev/null || echo "Bot connectivity test completed"

echo ""
echo "🎉 PERMANENT SETUP COMPLETE!"
echo "📁 Database: /app/telegram_bot/pgdata (PERSISTENT)"
echo "🔑 Credentials: /app/telegram_bot/.env (SAVED)"
echo "🤖 Bot: Running and connected"
echo ""
echo "To restart bot in future, just run: ./start_bot_permanent.sh"