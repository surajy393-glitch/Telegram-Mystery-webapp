#!/usr/bin/env python3
"""
Script to create Telegram Stars invoice links for LuvHive Premium (Multi-tier)
Run this once to generate the invoice slugs for all premium tiers
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram import Bot, LabeledPrice

# Premium tiers configuration
PREMIUM_TIERS = [
    {
        "name": "1 Week",
        "duration": "1 week",
        "stars": 100,
        "usd": "$1.99",
        "payload": "luvhive_premium_1week",
        "description": "Premium access for 1 week with all features unlocked"
    },
    {
        "name": "1 Month",
        "duration": "1 month",
        "stars": 250,
        "usd": "$3.99",
        "payload": "luvhive_premium_1month",
        "description": "Premium access for 1 month with all features unlocked"
    },
    {
        "name": "6 Months",
        "duration": "6 months",
        "stars": 600,
        "usd": "$9.99",
        "payload": "luvhive_premium_6months",
        "description": "Premium access for 6 months with all features unlocked"
    },
    {
        "name": "12 Months",
        "duration": "12 months",
        "stars": 1000,
        "usd": "$19.99",
        "payload": "luvhive_premium_12months",
        "description": "Premium access for 12 months with all features unlocked"
    }
]

async def create_all_premium_invoices():
    """Create Telegram Stars invoice links for all premium tiers"""
    
    # Get bot token from environment
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        print("❌ Error: BOT_TOKEN not found in environment")
        print("   Make sure .env file exists with BOT_TOKEN")
        return {}
    
    bot = Bot(token=bot_token)
    
    print("🚀 Creating Telegram Stars invoices for all LuvHive Premium tiers...")
    print("=" * 70)
    
    invoice_slugs = {}
    
    for tier in PREMIUM_TIERS:
        print(f"\n📦 Creating invoice for: {tier['name']} ({tier['stars']} Stars / {tier['usd']})")
        
        try:
            # Create invoice link
            invoice_link = await bot.create_invoice_link(
                title=f"LuvHive Premium - {tier['name']}",
                description=tier['description'],
                payload=tier['payload'],
                currency="XTR",  # Telegram Stars currency
                prices=[LabeledPrice(label=f"Premium - {tier['name']}", amount=tier['stars'])]
            )
            
            # Extract slug (part after $)
            if '$' in invoice_link:
                slug = invoice_link.split('$')[1]
                invoice_slugs[tier['duration']] = slug
                print(f"   ✅ Success! Slug: {slug}")
            else:
                print(f"   ⚠️  Warning: Could not extract slug from invoice link")
                print(f"   Full link: {invoice_link}")
                
        except Exception as e:
            print(f"   ❌ Error creating invoice: {e}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("📋 INVOICE SLUGS SUMMARY")
    print("=" * 70)
    print("\nAdd these to your frontend/.env file:\n")
    
    if '1 week' in invoice_slugs:
        print(f"REACT_APP_PREMIUM_INVOICE_SLUG_1WEEK={invoice_slugs['1 week']}")
    if '1 month' in invoice_slugs:
        print(f"REACT_APP_PREMIUM_INVOICE_SLUG_1MONTH={invoice_slugs['1 month']}")
    if '6 months' in invoice_slugs:
        print(f"REACT_APP_PREMIUM_INVOICE_SLUG_6MONTHS={invoice_slugs['6 months']}")
    if '12 months' in invoice_slugs:
        print(f"REACT_APP_PREMIUM_INVOICE_SLUG_12MONTHS={invoice_slugs['12 months']}")
    
    print("\n" + "=" * 70)
    
    return invoice_slugs

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the async function
    slugs = asyncio.run(create_all_premium_invoices())
    
    if slugs:
        print(f"\n✅ Success! Generated {len(slugs)} invoice slugs.")
        print(f"   Copy the environment variables above to your frontend/.env file")
    else:
        print(f"\n❌ Failed to create invoices. Check errors above.")
