#!/bin/bash
export BOT_TOKEN="8494034049:AAFnfoQO2mzJE-AEdI79l5s-i8ygnAf6Hzo"
export DATABASE_URL="postgresql://neondb_owner:npg_oVJba7TZXiW3@ep-lingering-sun-afnijqh1.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require"

cd /app/telegram_bot
python3 main.py
