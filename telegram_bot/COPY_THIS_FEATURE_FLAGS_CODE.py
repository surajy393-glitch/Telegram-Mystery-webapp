"""
Feature Flags - ACTUAL Bot Integration
Copy this code into your bot handlers
"""

# Add to telegram_bot/main.py or handlers

from utils.feature_flags import is_feature_enabled, set_feature_flag, get_all_flags

# Example 1: Check feature before executing
async def handle_fantasy_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fantasy match handler with feature flag"""
    
    # Check if feature is enabled
    if not await is_feature_enabled('fantasy_notifications'):
        await update.message.reply_text(
            "🔒 Fantasy Match is currently disabled by admin."
        )
        return
    
    # Continue with existing fantasy logic...
    # ... your fantasy match code here


# Example 2: Admin command to toggle features
async def cmd_admin_flags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command: /admin_flags [flag_name] [on/off]"""
    
    user_id = update.effective_user.id
    
    # Check admin (replace with your admin check)
    ADMIN_IDS = [123456789]  # Your admin user IDs
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Admin only")
        return
    
    if not context.args:
        # Show all flags
        flags = await get_all_flags()
        
        msg = "**🚩 Feature Flags:**\n\n"
        for flag_name, flag_data in flags.items():
            status = "✅" if flag_data['enabled'] else "❌"
            msg += f"{status} `{flag_name}`\n"
            msg += f"   _{flag_data['description']}_\n\n"
        
        msg += "\n**Usage:** `/admin_flags <flag> <on|off>`"
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    # Toggle flag
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /admin_flags <flag> <on|off>")
        return
    
    flag_name = context.args[0]
    new_state = context.args[1].lower() in ['on', 'true', '1', 'yes']
    
    await set_feature_flag(flag_name, new_state, f"admin_{user_id}")
    
    status = "✅ Enabled" if new_state else "❌ Disabled"
    await update.message.reply_text(
        f"**{status}** feature: `{flag_name}`",
        parse_mode='Markdown'
    )


# Example 3: Initialize feature flags on bot startup
async def init_feature_flags_on_startup(application):
    """Call this in bot's post_init"""
    from utils.feature_flags import init_feature_flags
    
    await init_feature_flags()
    
    # Set default states if needed
    # await set_feature_flag('fantasy_notifications', True, 'system')
    # await set_feature_flag('confession_roulette', True, 'system')
    
    print("✅ Feature flags initialized")


# To register in main.py:
# application.post_init = init_feature_flags_on_startup
# application.add_handler(CommandHandler("admin_flags", cmd_admin_flags))
