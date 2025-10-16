#!/bin/bash

echo "🤖 Starting LuvHive Telegram Bot..."

# Set credentials
export BOT_TOKEN="8494034049:AAEb5jiuYLUMmkjsIURx6RqhHJ4mj3bOI10"
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/luvhive_bot"

# Start minimal PostgreSQL if needed
if ! nc -z localhost 5432; then
    echo "📀 Starting PostgreSQL..."
    sudo -u postgres /usr/lib/postgresql/15/bin/pg_ctl start -D /var/lib/postgresql/15/main -l /tmp/postgres.log || echo "Using alternative method..."
fi

# Start the bot
echo "🚀 Launching bot..."
cd /app/telegram_bot
python main.py