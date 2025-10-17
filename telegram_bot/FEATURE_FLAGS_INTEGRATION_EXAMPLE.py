"""
Feature Flags Integration Example for Telegram Bot
Shows how to use centralized feature flags instead of bot_data
"""

# Example integration in fantasy_match.py or main.py

from utils.feature_flags import is_feature_enabled

# OLD WAY (what currently exists):
# context.application.bot_data.setdefault('fantasy_notif_mode', 'auto')

# NEW WAY (using feature flags):

async def cmd_fantasy_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to toggle fantasy notifications"""
    from utils.feature_flags import set_feature_flag, get_all_flags
    
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("⛔ Admin only command")
        return
    
    if not context.args:
        # Show current flags
        flags = await get_all_flags()
        msg = "**Feature Flags:**\n\n"
        for flag_name, flag_data in flags.items():
            status = "✅ Enabled" if flag_data['enabled'] else "❌ Disabled"
            msg += f"• {flag_name}: {status}\n"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    # Toggle flag
    flag_name = context.args[0]
    new_state = context.args[1].lower() == 'on' if len(context.args) > 1 else True
    
    await set_feature_flag(flag_name, new_state, f"admin_{user_id}")
    
    await update.message.reply_text(
        f"✅ Feature '{flag_name}' {'enabled' if new_state else 'disabled'}"
    )


async def handle_fantasy_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle fantasy match - now using feature flags"""
    
    # Check if feature is enabled
    if not await is_feature_enabled('fantasy_notifications'):
        await update.message.reply_text(
            "🔒 Fantasy Match feature is currently disabled."
        )
        return
    
    # Continue with fantasy logic...
    # ... existing code


# Initialize feature flags on startup
async def init_bot_features():
    """Initialize all bot feature flags"""
    from utils.feature_flags import init_feature_flags
    
    await init_feature_flags()
    
    # Set default values if needed
    # await set_feature_flag('fantasy_notifications', True, 'system')
    # await set_feature_flag('confession_roulette', True, 'system')
    # await set_feature_flag('naughty_wyr', True, 'system')


# In main.py startup:
async def post_init(application):
    """Called after bot initialization"""
    await init_bot_features()
    logger.info("Feature flags initialized")

# application.post_init = post_init
