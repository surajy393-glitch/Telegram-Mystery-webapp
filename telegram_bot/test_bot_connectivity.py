#!/usr/bin/env python3
"""
Test bot connectivity and age verification setup
"""
import asyncio
import os
from pathlib import Path

async def test_bot():
    # Load credentials
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value

    from telegram import Bot
    bot_token = os.environ.get('BOT_TOKEN')
    
    if not bot_token:
        print("❌ BOT_TOKEN not found")
        return
    
    try:
        bot = Bot(token=bot_token)
        me = await bot.get_me()
        print(f"✅ Bot connected successfully!")
        print(f"   Bot name: {me.first_name}")
        print(f"   Bot username: @{me.username}")
        print(f"   Bot ID: {me.id}")
        
        # Test database connection
        import registration
        with registration._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                print(f"✅ Database connected: {version}")
                
                # Check if age verification columns exist
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name IN ('age_verified', 'age_agreement_date')
                """)
                columns = [row[0] for row in cur.fetchall()]
                print(f"✅ Age verification columns: {columns}")
                
        print("🎉 Bot and age verification system are ready!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot())