#!/bin/bash

case "$1" in
    backup)
        echo "💾 Creating database backup..."
        mkdir -p /app/telegram_bot/backups
        sudo -u postgres pg_dump luvhive_bot > /app/telegram_bot/backups/backup_$(date +%Y%m%d_%H%M%S).sql
        echo "✅ Backup created in /app/telegram_bot/backups/"
        ;;
    restore)
        if [ -z "$2" ]; then
            echo "❌ Usage: $0 restore <backup_file>"
            echo "Available backups:"
            ls -la /app/telegram_bot/backups/*.sql 2>/dev/null || echo "No backups found"
            exit 1
        fi
        echo "🔄 Restoring database from $2..."
        sudo -u postgres dropdb luvhive_bot 2>/dev/null || echo "Database doesn't exist"
        sudo -u postgres createdb luvhive_bot
        sudo -u postgres psql luvhive_bot < "$2"
        echo "✅ Database restored"
        ;;
    status)
        echo "📊 SYSTEM STATUS:"
        echo "PostgreSQL: $(netstat -tlnp | grep 5432 >/dev/null && echo '✅ Running' || echo '❌ Not running')"
        echo "Bot: $(ps aux | grep 'python main.py' | grep -v grep >/dev/null && echo '✅ Running' || echo '❌ Not running')"
        echo "Data Directory: $([ -d /app/telegram_bot/pgdata ] && echo '✅ Exists' || echo '❌ Missing')"
        echo "Credentials: $([ -f /app/telegram_bot/.env ] && echo '✅ Saved' || echo '❌ Missing')"
        ;;
    *)
        echo "Usage: $0 {backup|restore <file>|status}"
        ;;
esac