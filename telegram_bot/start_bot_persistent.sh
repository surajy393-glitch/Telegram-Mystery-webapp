#!/bin/bash
# ============================================================================
# PERSISTENT DATA STARTUP SCRIPT
# ============================================================================
# This script ensures PostgreSQL data persists between container restarts
# by storing data in /app/postgres_data (mounted on persistent volume)
# ============================================================================

set -e

echo "🚀 Starting LuvHive Bot with Persistent Data..."
echo ""

# ============================================================================
# 1. ENSURE PERSISTENT DATA DIRECTORY EXISTS
# ============================================================================
echo "📁 Checking persistent data directory..."
if [ ! -d "/app/postgres_data" ]; then
    echo "   Creating /app/postgres_data..."
    mkdir -p /app/postgres_data
    chown -R postgres:postgres /app/postgres_data
    chmod 700 /app/postgres_data
    echo "   ✅ Created persistent data directory"
else
    echo "   ✅ Persistent data directory exists"
fi

# ============================================================================
# 2. CONFIGURE POSTGRESQL FOR PERSISTENT STORAGE
# ============================================================================
echo ""
echo "⚙️  Configuring PostgreSQL..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "   Installing PostgreSQL..."
    apt-get update -qq && apt-get install -y postgresql postgresql-contrib -qq
    echo "   ✅ PostgreSQL installed"
fi

# Update PostgreSQL config to use persistent directory
if grep -q "data_directory = '/var/lib/postgresql" /etc/postgresql/15/main/postgresql.conf; then
    echo "   Updating data_directory to /app/postgres_data..."
    sed -i "s|data_directory = '/var/lib/postgresql/15/main'|data_directory = '/app/postgres_data'|g" /etc/postgresql/15/main/postgresql.conf
    echo "   ✅ PostgreSQL configured for persistent storage"
fi

# Set trust authentication
sed -i 's/peer/trust/g' /etc/postgresql/15/main/pg_hba.conf
sed -i 's/md5/trust/g' /etc/postgresql/15/main/pg_hba.conf

# ============================================================================
# 3. INITIALIZE POSTGRESQL DATA IF NEEDED
# ============================================================================
echo ""
echo "🗄️  Checking PostgreSQL data..."

# Check if data directory is initialized
if [ ! -f "/app/postgres_data/PG_VERSION" ]; then
    echo "   Initializing PostgreSQL data directory..."
    su - postgres -c "/usr/lib/postgresql/15/bin/initdb -D /app/postgres_data"
    echo "   ✅ PostgreSQL data directory initialized"
else
    echo "   ✅ PostgreSQL data directory already initialized"
fi

# ============================================================================
# 4. START POSTGRESQL
# ============================================================================
echo ""
echo "🐘 Starting PostgreSQL..."
service postgresql stop 2>/dev/null || true
sleep 2
service postgresql start
sleep 3

if ps aux | grep postgres | grep -v grep > /dev/null; then
    echo "   ✅ PostgreSQL running"
else
    echo "   ❌ PostgreSQL failed to start"
    tail -20 /var/log/postgresql/postgresql-15-main.log
    exit 1
fi

# ============================================================================
# 5. CREATE DATABASE IF NOT EXISTS
# ============================================================================
echo ""
echo "💾 Checking database..."

# Check if database exists
if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw luvhive_bot; then
    echo "   ✅ Database luvhive_bot exists"
    
    # Count tables
    TABLE_COUNT=$(psql -U postgres -d luvhive_bot -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" 2>/dev/null || echo "0")
    echo "   📊 Current tables: $TABLE_COUNT"
else
    echo "   Creating database luvhive_bot..."
    psql -U postgres -c "CREATE DATABASE luvhive_bot;"
    
    # Import schema if DATABASE_COMPLETE.sql exists
    if [ -f "/app/telegram_bot/DATABASE_COMPLETE.sql" ]; then
        echo "   Importing database schema (131 tables)..."
        psql -U postgres -d luvhive_bot -f /app/telegram_bot/DATABASE_COMPLETE.sql > /dev/null 2>&1
        echo "   ✅ Database created and schema imported"
    else
        echo "   ✅ Database created (tables will be created by bot)"
    fi
fi

# Set password
psql -U postgres -c "ALTER USER postgres PASSWORD 'postgres123';" > /dev/null 2>&1

# ============================================================================
# 6. STOP EXISTING BOT
# ============================================================================
echo ""
echo "🛑 Stopping existing bot processes..."
pkill -f "python.*main.py" 2>/dev/null || true
sleep 2
echo "   ✅ Existing processes stopped"

# ============================================================================
# 7. START BOT
# ============================================================================
echo ""
echo "🤖 Starting LuvHive Bot..."
cd /app/telegram_bot

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | xargs)
    echo "   ✅ Environment variables loaded"
else
    echo "   ⚠️  No .env file found"
fi

# Start bot in background
nohup python3 main.py > bot.log 2>&1 &
sleep 6

# Check if bot is running
if ps aux | grep "python.*main.py" | grep -v grep > /dev/null; then
    echo "   ✅ Bot started successfully!"
    echo ""
    echo "📊 Bot Status:"
    ps aux | grep "python.*main.py" | grep -v grep | awk '{print "   PID: "$2", CPU: "$3"%, MEM: "$4"%"}'
    echo ""
    echo "📝 View logs: tail -f /app/telegram_bot/bot.log"
    echo "🛑 Stop bot: pkill -f 'python.*main.py'"
    echo ""
    echo "✅ PERSISTENT DATA LOCATION: /app/postgres_data"
    echo "   Your data will SURVIVE container restarts!"
else
    echo "   ❌ Bot failed to start"
    echo ""
    echo "Last 20 lines of bot log:"
    tail -20 /app/telegram_bot/bot.log
    exit 1
fi

echo ""
echo "🎉 Startup complete!"
