#!/usr/bin/env python3
"""
Create Telegram Stars invoice and get the FULL URL for webapp
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram import Bot, LabeledPrice

async def create_premium_invoice():
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        print("❌ Error: BOT_TOKEN not found")
        return None
    
    bot = Bot(token=bot_token)
    
    print("🚀 Creating Telegram Stars invoice...")
    
    try:
        # Create invoice link
        invoice_url = await bot.create_invoice_link(
            title="LuvHive Premium - 1 Month",
            description="Unlimited chats, photos/videos, read receipts, priority placement, and bot filters",
            payload="luvhive_premium_1month",
            currency="XTR",
            prices=[LabeledPrice(label="Premium - 1 Month", amount=250)]
        )
        
        print(f"\n✅ Invoice Created Successfully!")
        print(f"📋 Full Invoice URL: {invoice_url}")
        print(f"\n📝 Add this to your webapp .env file:")
        print(f"   REACT_APP_PREMIUM_INVOICE_URL={invoice_url}")
        print(f"\n⚠️  Use the FULL URL, not just the slug!")
        
        return invoice_url
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    url = asyncio.run(create_premium_invoice())
    
    if url:
        print(f"\n✅ Success! Use the full URL above.")
    else:
        print(f"\n❌ Failed to create invoice.")
