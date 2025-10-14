#!/bin/bash

echo "🔧 Setting up PERMANENT database solution..."

# Create permanent PostgreSQL data directory
PGDATA_DIR="/app/telegram_bot/pgdata"
mkdir -p $PGDATA_DIR
chown -R postgres:postgres $PGDATA_DIR 2>/dev/null || echo "Creating postgres user..."

# Create postgres user if not exists
id -u postgres &>/dev/null || useradd -r -s /bin/bash postgres

# Set ownership
chown -R postgres:postgres $PGDATA_DIR

# Initialize database if not exists
if [ ! -f "$PGDATA_DIR/PG_VERSION" ]; then
    echo "🆕 Initializing new PostgreSQL cluster..."
    sudo -u postgres /usr/lib/postgresql/15/bin/initdb -D $PGDATA_DIR --auth-local=trust --auth-host=trust
    echo "✅ Database initialized"
fi

# Create startup script
cat > $PGDATA_DIR/start_postgres.sh << 'EOF'
#!/bin/bash
export PGDATA=/app/telegram_bot/pgdata
/usr/lib/postgresql/15/bin/postgres -D $PGDATA -p 5432 > /tmp/postgres.log 2>&1 &
echo "PostgreSQL started, PID: $!"
EOF

chmod +x $PGDATA_DIR/start_postgres.sh
chown postgres:postgres $PGDATA_DIR/start_postgres.sh

# Start PostgreSQL
echo "🚀 Starting PostgreSQL..."
sudo -u postgres $PGDATA_DIR/start_postgres.sh

# Wait for startup
sleep 5

# Create database if not exists
sudo -u postgres createdb luvhive_bot 2>/dev/null || echo "Database already exists"

echo "✅ Permanent PostgreSQL setup complete!"
echo "📁 Data directory: $PGDATA_DIR"
echo "🔧 Startup script: $PGDATA_DIR/start_postgres.sh"