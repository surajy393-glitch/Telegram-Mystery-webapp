#!/usr/bin/env python3
"""
Startup script for the Complete Instagram-Style Social Platform Telegram Bot
Run this to start the full-featured Telegram bot with all social features
"""
import subprocess
import sys
import os
from pathlib import Path

# Change to the backend directory where main_bot.py is located
backend_dir = Path(__file__).parent / "backend"
os.chdir(backend_dir)

# Add backend directory to Python path
sys.path.insert(0, str(backend_dir))

print("🚀 Starting Complete Social Platform Telegram Bot...")
print("💕 Features: Dating/Matching, Stories, Posts, Games, Premium")
print("🌐 Web App URL: https://github-repo-view-2.preview.emergentagent.com")
print("🎮 Bot Features: Registration, Profile, Matching, Fun Games")
print("=" * 60)

try:
    # Run the enhanced bot
    subprocess.run([sys.executable, "enhanced_bot.py"], check=True)
except KeyboardInterrupt:
    print("\n🛑 Bot stopped by user")
except Exception as e:
    print(f"❌ Bot crashed: {e}")
    sys.exit(1)