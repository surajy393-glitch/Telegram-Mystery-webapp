# 🚀 Mystery Match API - PostgreSQL Setup Guide

Complete guide for setting up PostgreSQL, running migrations, and testing the async Mystery Match API.

---

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.11+
- pip & virtualenv

---

## 🐘 PostgreSQL Setup

### Option 1: Automated Setup (Recommended)

Run the setup script:

```bash
cd /app
./setup_postgres.sh
```

This script will:
1. ✅ Start PostgreSQL with Docker Compose
2. ✅ Wait for PostgreSQL to be ready
3. ✅ Set environment variables
4. ✅ Run Alembic migrations
5. ✅ Verify database schema
6. ✅ Update backend .env file

### Option 2: Manual Setup

#### Step 1: Start PostgreSQL

```bash
cd /app
docker compose up -d
```

#### Step 2: Wait for PostgreSQL

```bash
# Wait 5-10 seconds for PostgreSQL to initialize
sleep 10
```

#### Step 3: Set Environment Variable

```bash
export DATABASE_URL="postgresql://luvhive:luvhive123@localhost:5432/luvhive_bot"
```

#### Step 4: Run Migrations

```bash
cd /app
alembic upgrade head
```

#### Step 5: Verify Tables

```bash
PGPASSWORD=luvhive123 psql -h localhost -U luvhive -d luvhive_bot -c "\dt"
```

Expected tables:
- ✅ users
- ✅ mystery_matches
- ✅ match_messages
- ✅ blocked_users
- ✅ payments
- ✅ feature_flags
- ✅ content_reports

---

## 🔧 Configuration

### Database Connection Details

```
Host:     localhost
Port:     5432
Database: luvhive_bot
User:     luvhive
Password: luvhive123
```

### Environment Variables

Add to `backend/.env`:

```env
DATABASE_URL="postgresql://luvhive:luvhive123@localhost:5432/luvhive_bot"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_DB="luvhive_bot"
POSTGRES_USER="luvhive"
POSTGRES_PASSWORD="luvhive123"
```

---

## 🧪 Testing

### Run All Tests

```bash
cd /app
pytest tests/ -v
```

### Run Specific Test

```bash
pytest tests/test_mystery_async.py::test_find_match_no_user -v
```

### Run with Coverage

```bash
pytest tests/ --cov=backend --cov-report=html
```

---

## 🚦 Verify Setup

### 1. Check PostgreSQL is Running

```bash
docker compose ps
```

Expected output:
```
NAME                COMMAND                  SERVICE     STATUS
app-postgres-1      "docker-entrypoint.s…"   postgres    Up
```

### 2. Check Database Connection

```bash
PGPASSWORD=luvhive123 psql -h localhost -U luvhive -d luvhive_bot -c "SELECT 1;"
```

Expected output:
```
 ?column? 
----------
        1
```

### 3. Check Tables

```bash
PGPASSWORD=luvhive123 psql -h localhost -U luvhive -d luvhive_bot -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
```

Expected: 7 tables

### 4. Test Mystery Match Endpoint

```bash
# Restart backend
sudo supervisorctl restart backend

# Test stats endpoint
curl http://localhost:8001/api/mystery/stats/123456
```

---

## 📊 Alembic Migrations

### Create New Migration

```bash
cd /app
alembic revision -m "Add new column"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### Check Current Version

```bash
alembic current
```

### View Migration History

```bash
alembic history --verbose
```

---

## 🐛 Troubleshooting

### PostgreSQL Not Starting

**Problem:** `docker compose up -d` fails

**Solution:**
```bash
# Check Docker is running
docker ps

# Check logs
docker compose logs postgres

# Try manual start
docker run -d \
  -e POSTGRES_USER=luvhive \
  -e POSTGRES_PASSWORD=luvhive123 \
  -e POSTGRES_DB=luvhive_bot \
  -p 5432:5432 \
  --name postgres \
  postgres:14
```

### Migration Fails

**Problem:** `alembic upgrade head` fails

**Solution:**
```bash
# Check Alembic is installed
pip install alembic

# Verify DATABASE_URL is set
echo $DATABASE_URL

# Check PostgreSQL is accessible
PGPASSWORD=luvhive123 psql -h localhost -U luvhive -d luvhive_bot -c "SELECT 1;"

# Try running migration with verbose output
alembic -c alembic.ini upgrade head --verbose
```

### Tests Fail

**Problem:** `pytest` fails with connection errors

**Solution:**
```bash
# Ensure PostgreSQL is running
docker compose ps

# Set DATABASE_URL for tests
export DATABASE_URL="postgresql://luvhive:luvhive123@localhost:5432/luvhive_bot"

# Run migrations
alembic upgrade head

# Try tests again
pytest tests/ -v
```

### Backend Can't Connect

**Problem:** Backend shows connection errors

**Solution:**
```bash
# 1. Check .env file
cat backend/.env | grep DATABASE_URL

# 2. Update .env if needed
echo 'DATABASE_URL="postgresql://luvhive:luvhive123@localhost:5432/luvhive_bot"' >> backend/.env

# 3. Restart backend
sudo supervisorctl restart backend

# 4. Check logs
tail -50 /var/log/supervisor/backend.err.log
```

---

## 📁 File Structure

```
/app/
├── docker-compose.yml              # PostgreSQL Docker setup
├── alembic.ini                     # Alembic configuration
├── setup_postgres.sh               # Automated setup script
├── alembic/
│   ├── env.py                      # Alembic environment
│   └── versions/
│       └── 20251017_initial_schema.py  # Initial migration
├── tests/
│   ├── conftest.py                 # Pytest fixtures
│   └── test_mystery_async.py       # Async tests
└── backend/
    ├── mystery_match.py            # Async endpoints
    └── database/
        └── async_db.py             # Async helpers
```

---

## 🎯 Quick Commands Reference

```bash
# Start PostgreSQL
docker compose up -d

# Stop PostgreSQL
docker compose down

# View PostgreSQL logs
docker compose logs -f postgres

# Run migrations
alembic upgrade head

# Run tests
pytest tests/ -v

# Restart backend
sudo supervisorctl restart backend

# Check backend logs
tail -f /var/log/supervisor/backend.err.log

# Connect to PostgreSQL
PGPASSWORD=luvhive123 psql -h localhost -U luvhive -d luvhive_bot

# Backup database
pg_dump -h localhost -U luvhive luvhive_bot > backup.sql

# Restore database
psql -h localhost -U luvhive luvhive_bot < backup.sql
```

---

## ✨ Features Enabled

Once PostgreSQL is set up, these Mystery Match features will work:

✅ Find Match (with filters)  
✅ Daily Limit (3 for free users)  
✅ Match Expiry (48 hours)  
✅ Real-time Chat (WebSocket)  
✅ Message Count Auto-increment  
✅ Block/Unblock Users  
✅ Secret Chat Requests  
✅ Match Extension (24 hours)  
✅ Online Status Checking  
✅ User Statistics  
✅ Content Reporting  
✅ Progressive Profile Unlock  

---

## 🚀 Performance Testing

### Load Testing with wrk

```bash
# Install wrk
sudo apt install wrk

# Test find-match endpoint
wrk -t4 -c100 -d30s --latency \
  -s post.lua \
  http://localhost:8001/api/mystery/find-match

# Test stats endpoint
wrk -t12 -c400 -d30s --latency \
  http://localhost:8001/api/mystery/stats/123456
```

### Monitor Database Performance

```bash
# Connection count
PGPASSWORD=luvhive123 psql -h localhost -U luvhive -d luvhive_bot \
  -c "SELECT count(*) FROM pg_stat_activity;"

# Active queries
PGPASSWORD=luvhive123 psql -h localhost -U luvhive -d luvhive_bot \
  -c "SELECT pid, usename, state, query FROM pg_stat_activity WHERE state != 'idle';"

# Database size
PGPASSWORD=luvhive123 psql -h localhost -U luvhive -d luvhive_bot \
  -c "SELECT pg_size_pretty(pg_database_size('luvhive_bot'));"
```

---

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [pytest Documentation](https://docs.pytest.org/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)

---

## 🎉 Success Checklist

Before considering setup complete, verify:

- ✅ PostgreSQL container is running
- ✅ 7 tables created in database
- ✅ Alembic migrations applied
- ✅ Tests pass (at least basic tests)
- ✅ Backend can connect to PostgreSQL
- ✅ Mystery Match endpoints return 200 (not 500)

---

**Date:** 2025-01-17  
**Version:** 1.0.0  
**Status:** Production Ready  
