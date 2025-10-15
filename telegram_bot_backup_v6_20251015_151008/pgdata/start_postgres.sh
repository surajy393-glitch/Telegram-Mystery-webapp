#!/bin/bash
export PGDATA=/app/telegram_bot/pgdata
/usr/lib/postgresql/15/bin/postgres -D $PGDATA -p 5432 > /tmp/postgres.log 2>&1 &
echo "PostgreSQL started, PID: $!"
