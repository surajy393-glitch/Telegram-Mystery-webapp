# 🔐 Secure Telegram Authentication Setup Guide

## 🚨 Current Status: DEVELOPMENT MODE
The application is currently using **mock Telegram authentication** for development. For production, follow this guide to implement **real secure Telegram authentication**.

## 🎯 What You'll Get After Setup
✅ **Real Telegram verification** - Users must actually authorize through Telegram  
✅ **Secure hash validation** - Prevents authentication spoofing attacks  
✅ **Anti-replay protection** - Prevents reuse of old authentication tokens  
✅ **Production-grade security** - Follows Telegram's official security guidelines  

---

## 📋 Prerequisites

1. **Telegram account** for creating a bot
2. **Domain with HTTPS** (required for production)
3. **Access to backend environment variables**

---

## 🤖 Step 1: Create Telegram Bot

### 1.1 Message BotFather
1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "LuvHive")
4. Choose a unique username ending in "bot" (e.g., "LuvHiveBot")
5. **Save the bot token** - you'll need it later

### 1.2 Configure Bot Domain
1. Send `/setdomain` to @BotFather
2. Select your bot
3. Enter your domain (e.g., `yourdomain.com`)

---

## 🔧 Step 2: Backend Configuration

### 2.1 Add Bot Token to Environment
Add to `/app/backend/.env`:
```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_FROM_BOTFATHER"
```

### 2.2 Restart Backend
```bash
sudo supervisorctl restart backend
```

### 2.3 Verify Configuration
Check that the backend accepts the new environment variable by testing:
```bash
curl -X GET "YOUR_BACKEND_URL/api/health"
```

---

## 🌐 Step 3: Frontend Integration

### 3.1 Replace Mock Authentication (LoginPage.js)

Replace the mock implementation in `/app/frontend/src/pages/LoginPage.js`:

```javascript
const handleTelegramAuth = async () => {
  setTelegramLoading(true);
  
  // Create Telegram Login Widget
  const script = document.createElement('script');
  script.async = true;
  script.src = 'https://telegram.org/js/telegram-widget.js?22';
  script.setAttribute('data-telegram-login', 'YourBotUsername'); // Replace with your bot username
  script.setAttribute('data-size', 'large');
  script.setAttribute('data-auth-url', `${window.location.origin}/auth/telegram-callback`);
  script.setAttribute('data-request-access', 'write');
  
  document.body.appendChild(script);
  
  // Handle Telegram callback
  window.handleTelegramCallback = async (user) => {
    try {
      const response = await axios.post(`${API}/auth/telegram`, user);
      onLogin(response.data.access_token, response.data.user);
      toast({
        title: "Success!",
        description: "Successfully logged in with Telegram",
      });
      navigate("/home");
    } catch (error) {
      toast({
        title: "Authentication Failed",
        description: error.response?.data?.detail || "Telegram authentication failed",
        variant: "destructive"
      });
    } finally {
      setTelegramLoading(false);
    }
  };
};
```

### 3.2 Add Callback Handler
Create `/app/frontend/src/pages/TelegramCallback.js`:

```javascript
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const TelegramCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const telegramData = {};
    
    // Extract Telegram authentication data from URL parameters
    ['id', 'first_name', 'last_name', 'username', 'photo_url', 'auth_date', 'hash'].forEach(key => {
      if (urlParams.has(key)) {
        telegramData[key] = urlParams.get(key);
      }
    });

    if (telegramData.id && window.parent.handleTelegramCallback) {
      window.parent.handleTelegramCallback(telegramData);
    } else {
      navigate('/login');
    }
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-pink-500 mx-auto"></div>
        <p className="mt-4 text-gray-600">Completing Telegram authentication...</p>
      </div>
    </div>
  );
};

export default TelegramCallback;
```

---

## 🧪 Step 4: Testing

### 4.1 Test Hash Verification
Run the backend test to verify security implementation:
```bash
cd /app
python test_telegram_auth.py
```

### 4.2 Test User Flow
1. Go to your login page
2. Click "Continue with Telegram"
3. Verify you're redirected to Telegram authorization
4. Complete authorization
5. Verify you're logged into LuvHive

---

## 🚀 Step 5: Production Deployment

### 5.1 HTTPS Requirement
- Telegram Login Widget **requires HTTPS** in production
- Ensure your domain has a valid SSL certificate

### 5.2 Security Checklist
- ✅ Bot token stored securely in environment variables
- ✅ Hash verification enabled in backend
- ✅ Domain configured with @BotFather
- ✅ HTTPS enabled for production domain
- ✅ Rate limiting implemented on authentication endpoints

### 5.3 Monitoring
Set up monitoring for:
- Failed hash verification attempts
- Unusual authentication patterns
- Backend errors in authentication flow

---

## 🔒 Security Features Implemented

### Hash Verification
- **Function**: `verify_telegram_hash()` in `server.py`
- **Algorithm**: HMAC-SHA256 using bot token as secret
- **Purpose**: Prevents authentication data tampering

### Timestamp Validation
- **Check**: Authentication data must be within 24 hours
- **Purpose**: Prevents replay attacks with old tokens

### Constant-Time Comparison
- **Implementation**: `hmac.compare_digest()`
- **Purpose**: Prevents timing attacks on hash comparison

---

## 🆘 Troubleshooting

### Common Issues

**Error: "Telegram bot not configured"**
- Solution: Add `TELEGRAM_BOT_TOKEN` to backend `.env` file

**Error: "Invalid Telegram authentication data"**
- Solution: Verify bot username in frontend matches your actual bot

**Telegram widget not loading**
- Solution: Ensure HTTPS is enabled for production domains

**Hash verification failing**
- Solution: Check that bot token is correct and matches the bot used in widget

### Debug Mode
Enable debug logging by adding to backend:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 Additional Resources

- [Telegram Login Widget Documentation](https://core.telegram.org/widgets/login)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Security Best Practices](https://core.telegram.org/widgets/login#checking-authorization)

---

## ✅ Implementation Checklist

- [ ] Create Telegram bot with @BotFather
- [ ] Add `TELEGRAM_BOT_TOKEN` to backend environment
- [ ] Replace mock authentication in frontend
- [ ] Add Telegram callback handler
- [ ] Test authentication flow
- [ ] Configure domain with @BotFather
- [ ] Enable HTTPS for production
- [ ] Monitor authentication logs

**Once completed, your LuvHive app will have enterprise-grade Telegram authentication! 🎉**