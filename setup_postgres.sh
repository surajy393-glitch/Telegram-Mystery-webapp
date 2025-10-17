#!/bin/bash

# Mystery Match PostgreSQL Setup Script
# This script sets up PostgreSQL, runs migrations, and prepares the environment

set -e

echo "🚀 Mystery Match PostgreSQL Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Start PostgreSQL with Docker
echo -e "${YELLOW}Step 1: Starting PostgreSQL with Docker Compose...${NC}"
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
    echo -e "${GREEN}✅ PostgreSQL started successfully${NC}"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    docker compose up -d
    echo -e "${GREEN}✅ PostgreSQL started successfully${NC}"
else
    echo -e "${RED}❌ Docker or Docker Compose not found. Please install Docker first.${NC}"
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo ""

# Step 2: Wait for PostgreSQL to be ready
echo -e "${YELLOW}Step 2: Waiting for PostgreSQL to be ready...${NC}"
sleep 5

# Check if PostgreSQL is accessible
if command -v psql &> /dev/null; then
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if PGPASSWORD=luvhive123 psql -h localhost -U luvhive -d luvhive_bot -c "SELECT 1;" &> /dev/null; then
            echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
            break
        fi
        attempt=$((attempt + 1))
        echo "   Waiting... ($attempt/$max_attempts)"
        sleep 1
    done
    
    if [ $attempt -eq $max_attempts ]; then
        echo -e "${RED}❌ PostgreSQL did not become ready in time${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  psql not found. Assuming PostgreSQL is running...${NC}"
    sleep 5
fi

echo ""

# Step 3: Set DATABASE_URL environment variable
echo -e "${YELLOW}Step 3: Setting up environment variables...${NC}"
export DATABASE_URL="postgresql://luvhive:luvhive123@localhost:5432/luvhive_bot"
echo "   DATABASE_URL=$DATABASE_URL"
echo -e "${GREEN}✅ Environment variables set${NC}"

echo ""

# Step 4: Run Alembic migrations
echo -e "${YELLOW}Step 4: Running Alembic migrations...${NC}"
cd /app
if command -v alembic &> /dev/null; then
    alembic upgrade head
    echo -e "${GREEN}✅ Migrations applied successfully${NC}"
else
    echo -e "${RED}❌ Alembic not found. Installing...${NC}"
    pip install alembic
    alembic upgrade head
    echo -e "${GREEN}✅ Migrations applied successfully${NC}"
fi

echo ""

# Step 5: Verify tables
echo -e "${YELLOW}Step 5: Verifying database schema...${NC}"
if command -v psql &> /dev/null; then
    TABLES=$(PGPASSWORD=luvhive123 psql -h localhost -U luvhive -d luvhive_bot -t -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';" 2>/dev/null | wc -l)
    if [ "$TABLES" -gt 0 ]; then
        echo -e "${GREEN}✅ Found $TABLES tables in database${NC}"
        echo ""
        echo "Tables created:"
        PGPASSWORD=luvhive123 psql -h localhost -U luvhive -d luvhive_bot -c "\dt" 2>/dev/null || echo "   (Unable to list tables)"
    else
        echo -e "${RED}❌ No tables found. Migration may have failed.${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Cannot verify tables without psql. Please check manually.${NC}"
fi

echo ""

# Step 6: Update backend .env file
echo -e "${YELLOW}Step 6: Updating backend .env file...${NC}"
ENV_FILE="/app/backend/.env"
if [ -f "$ENV_FILE" ]; then
    # Update or add DATABASE_URL
    if grep -q "^DATABASE_URL=" "$ENV_FILE"; then
        sed -i 's|^DATABASE_URL=.*|DATABASE_URL="postgresql://luvhive:luvhive123@localhost:5432/luvhive_bot"|' "$ENV_FILE"
    else
        echo 'DATABASE_URL="postgresql://luvhive:luvhive123@localhost:5432/luvhive_bot"' >> "$ENV_FILE"
    fi
    
    # Update POSTGRES_* variables
    sed -i 's|^POSTGRES_HOST=.*|POSTGRES_HOST="localhost"|' "$ENV_FILE"
    sed -i 's|^POSTGRES_USER=.*|POSTGRES_USER="luvhive"|' "$ENV_FILE"
    sed -i 's|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD="luvhive123"|' "$ENV_FILE"
    sed -i 's|^POSTGRES_DB=.*|POSTGRES_DB="luvhive_bot"|' "$ENV_FILE"
    
    echo -e "${GREEN}✅ Backend .env updated${NC}"
else
    echo -e "${YELLOW}⚠️  Backend .env not found at $ENV_FILE${NC}"
fi

echo ""
echo "=================================="
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Restart your backend server:"
echo "   sudo supervisorctl restart backend"
echo ""
echo "2. Run tests:"
echo "   cd /app && pytest tests/ -v"
echo ""
echo "3. Check Mystery Match endpoints:"
echo "   curl http://localhost:8001/api/mystery/stats/123456"
echo ""
echo "PostgreSQL Info:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: luvhive_bot"
echo "   User: luvhive"
echo "   Password: luvhive123"
echo ""
