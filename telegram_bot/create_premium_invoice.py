#!/usr/bin/env python3
"""
Script to create Telegram Stars invoice link for LuvHive Premium
Run this once to generate the invoice slug for the webapp
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram import Bot, LabeledPrice

async def create_premium_invoice():
    """Create Telegram Stars invoice and return the slug"""
    
    # Get bot token from environment
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        print("❌ Error: BOT_TOKEN not found in environment")
        print("   Make sure .env file exists with BOT_TOKEN")
        return None
    
    bot = Bot(token=bot_token)
    
    print("🚀 Creating Telegram Stars invoice for LuvHive Premium...")
    
    try:
        # Create invoice link
        invoice_link = await bot.create_invoice_link(
            title="LuvHive Premium - 1 Month",
            description="Unlimited chats, photos/videos, read receipts, priority placement, and bot filters",
            payload="luvhive_premium_1month",
            currency="XTR",  # Telegram Stars currency
            prices=[LabeledPrice(label="Premium - 1 Month", amount=250)]  # 250 Stars
        )
        
        print(f"\n✅ Invoice Link Created Successfully!")
        print(f"📋 Full Link: {invoice_link}")
        
        # Extract slug (part after $)
        if '$' in invoice_link:
            slug = invoice_link.split('$')[1]
            print(f"\n🎯 Invoice Slug: {slug}")
            print(f"\n📝 Add this to your webapp .env file:")
            print(f"   REACT_APP_PREMIUM_INVOICE_SLUG={slug}")
            return slug
        else:
            print("⚠️  Warning: Could not extract slug from invoice link")
            return None
            
    except Exception as e:
        print(f"❌ Error creating invoice: {e}")
        return None

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the async function
    slug = asyncio.run(create_premium_invoice())
    
    if slug:
        print(f"\n✅ Success! Use the slug above in your webapp configuration.")
    else:
        print(f"\n❌ Failed to create invoice. Check errors above.")
