#!/usr/bin/env python3
"""
Start the Telegram bot with saved credentials
"""
import os
from pathlib import Path

def load_env():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded from .env file")
    else:
        print("❌ .env file not found")

if __name__ == "__main__":
    # Load saved credentials
    load_env()
    
    # Check if credentials are loaded
    bot_token = os.environ.get('BOT_TOKEN')
    database_url = os.environ.get('DATABASE_URL')
    
    if bot_token and database_url:
        print(f"✅ BOT_TOKEN: {bot_token[:10]}...")
        print(f"✅ DATABASE_URL: {database_url[:30]}...")
        print("🤖 Starting Telegram bot...")
        
        # Import and run main
        from main import main
        main()
    else:
        print("❌ Missing credentials in .env file")
        print("Required: BOT_TOKEN and DATABASE_URL")