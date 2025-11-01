# LuvHive - Instagram-Style Dating & Social Webapp for Telegram Bot

## 🎭 Overview

LuvHive is a beautiful, Instagram-style social and dating webapp designed to work seamlessly with your Telegram bot. It features:

- **Light Pink & White Theme**: Beautiful, modern design
- **Anonymous Social Features**: Stories (24h), Posts, User Profiles
- **Premium Chat System**: Free browsing, premium required for messaging
- **Telegram Bot Integration**: Link accounts via unique codes
- **Responsive Design**: Works perfectly on all devices

## 🌟 Features

### ✨ Core Features
1. **Landing Page** - Welcome page with app information
2. **Multi-Step Registration** - Full Name → Username → Age → Gender → Password → Bio → Profile Image
3. **Login/Logout System** - Secure JWT authentication
4. **Instagram-Style Stories** - 24-hour expiring stories with circular avatars
5. **Posts Feed** - Like, comment, and share posts
6. **User Profiles** - View profile, bio, and connection status
7. **Chat System** - Premium-only messaging with popup for upgrades
8. **Telegram Integration** - Link webapp to Telegram bot account

### 🔐 Premium Features
- Unlimited chat access
- Premium badge display
- Exclusive features (extensible)

## 🏗️ Tech Stack

**Frontend:**
- React 19
- Tailwind CSS
- Shadcn UI Components
- Axios for API calls
- React Router for navigation

**Backend:**
- FastAPI (Python)
- MongoDB (via Motor async driver)
- JWT Authentication
- Bcrypt password hashing
- CORS enabled

**Database Collections:**
- `users` - User accounts and profiles
- `stories` - 24-hour temporary stories
- `posts` - Permanent posts with likes/comments
- `messages` - Chat messages
- `telegram_links` - Telegram account linking codes

## 📁 Project Structure

```
/app/
├── backend/
│   ├── server.py           # Main FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component with routing
│   │   ├── App.css        # Global styles
│   │   ├── pages/
│   │   │   ├── LandingPage.js    # Welcome page
│   │   │   ├── RegisterPage.js   # Multi-step registration
│   │   │   ├── LoginPage.js      # Login page
│   │   │   ├── HomePage.js       # Stories + Posts feed
│   │   │   ├── ProfilePage.js    # User profile & discover
│   │   │   └── ChatPage.js       # Chat interface
│   │   └── components/ui/        # Shadcn UI components
│   └── .env               # Frontend environment variables
└── README_LUVHIVE.md      # This file
```

## 🚀 Getting Started

### Prerequisites
- MongoDB running on localhost:27017
- Node.js and Yarn installed
- Python 3.11+ with pip

### Installation

1. **Backend Setup:**
```bash
cd /app/backend
pip install -r requirements.txt
```

2. **Frontend Setup:**
```bash
cd /app/frontend
yarn install
```

3. **Environment Variables:**

Backend (`.env`):
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="luvhive_database"
CORS_ORIGINS="*"
JWT_SECRET="luvhive-secret-key-change-in-production-2024"
```

Frontend (`.env`):
```env
REACT_APP_BACKEND_URL=https://github-repo-view-2.preview.emergentagent.com
WDS_SOCKET_PORT=443
```

### Running the Application

Services are managed by supervisor:

```bash
# Check status
sudo supervisorctl status

# Restart services
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart all
```

Access the app at: `https://github-repo-view-2.preview.emergentagent.com`

## 🤖 Telegram Bot Integration

### How to Integrate with Your Telegram Bot

#### 1. Generate Link Codes in Your Bot

When a user wants to link their account, your Telegram bot should:

```python
import uuid
from pymongo import MongoClient

# Generate unique code
link_code = str(uuid.uuid4())[:8]  # e.g., "a1b2c3d4"

# Store in database
db.telegram_links.insert_one({
    "code": link_code,
    "telegramUserId": str(telegram_user_id),
    "createdAt": datetime.utcnow()
})

# Send to user
await bot.send_message(
    chat_id=telegram_user_id,
    text=f"Your link code: {link_code}\nEnter this code in the webapp to link your account."
)
```

#### 2. User Links Account in Webapp

User enters the code in the webapp, which calls:
```
POST /api/telegram/link
Body: { "code": "a1b2c3d4" }
Headers: { "Authorization": "Bearer <jwt_token>" }
```

#### 3. Premium Purchase Flow

**In Your Telegram Bot:**

```python
# When user purchases premium
await db.users.update_one(
    {"telegramUserId": str(telegram_user_id)},
    {"$set": {"isPremium": True}}
)
```

**In Webapp:**
- Non-premium users see "Premium Chat" button
- Clicking opens popup: "Buy Premium from Bot to Use Chat Service"
- "Open Telegram Bot" button redirects to your bot
- After purchase in bot, user can chat in webapp

#### 4. Update Bot Link in Code

In `/app/frontend/src/pages/ProfilePage.js` and `/app/frontend/src/pages/ChatPage.js`:

```javascript
// Change this line (appears twice):
onClick={() => window.open("https://t.me/your_bot_username", "_blank")}

// Replace with your actual bot username:
onClick={() => window.open("https://t.me/YOUR_BOT_USERNAME_HERE", "_blank")}
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Login with username/password
- `GET /api/auth/me` - Get current user info
- `PUT /api/auth/profile` - Update bio and profile image

### Telegram Integration
- `POST /api/telegram/link` - Link Telegram account via code

### Stories
- `POST /api/stories/create` - Create new story
- `GET /api/stories/feed` - Get all active stories (< 24h old)

### Posts
- `POST /api/posts/create` - Create new post
- `GET /api/posts/feed` - Get all posts
- `POST /api/posts/{post_id}/like` - Like/unlike a post

### Chat
- `POST /api/chat/send` - Send message (premium only)
- `GET /api/chat/messages/{userId}` - Get conversation with user

### Users
- `GET /api/users/list` - Get all users (for discovery)

## 💾 Media Storage Strategy (for 100k+ Users)

### Recommended: Telegram CDN Method

**Store only `file_id` in MongoDB, not the actual media:**

1. When user uploads media in webapp:
   - Send media to your Telegram bot
   - Bot uploads to a Telegram channel
   - Telegram returns `file_id`
   - Store `file_id` in MongoDB

2. When displaying media:
   - Fetch from Telegram using `file_id`
   - Telegram's CDN delivers the media

**Benefits:**
- ✅ Zero storage costs
- ✅ Scales infinitely
- ✅ Fast global CDN delivery
- ✅ No bandwidth limits

**Implementation Example:**

```python
# In your Telegram bot
async def save_media(file_id):
    # Store in your storage channel
    await bot.forward_message(
        chat_id=STORAGE_CHANNEL_ID,
        from_chat_id=user_chat_id,
        message_id=message_id
    )
    return file_id

# In webapp backend
async def create_story(story_data):
    # story_data.mediaUrl contains file_id from Telegram
    story = Story(
        mediaType=story_data.mediaType,
        mediaUrl=story_data.mediaUrl,  # This is file_id
        caption=story_data.caption
    )
    await db.stories.insert_one(story.dict())
```

### Alternative: Base64 Storage (Quick Start)

For MVP/testing, you can store images as Base64 in MongoDB:
- Works immediately without Telegram integration
- Good for < 1000 users
- Switch to Telegram CDN method for scale

## 🎨 Design Customization

### Color Theme

Current: Light Pink & White

To change colors, update in `/app/frontend/src/App.css` and Tailwind classes:

```css
/* Current pink theme */
background: linear-gradient(135deg, #fce4ec 0%, #ffffff 50%, #fce4ec 100%);

/* Primary: pink-500, pink-600 */
/* Accent: rose-500, rose-600 */
```

### Fonts

- **Headings**: Playfair Display (elegant serif)
- **Body**: Manrope (clean sans-serif)

Change in `/app/frontend/src/App.css`:
```css
@import url('https://fonts.googleapis.com/css2?family=YourFont&display=swap');
```

## 🔒 Security Notes

1. **Change JWT Secret in Production:**
   Update `JWT_SECRET` in `/app/backend/.env`

2. **HTTPS Only:**
   Ensure production runs on HTTPS

3. **Rate Limiting:**
   Consider adding rate limiting for API endpoints

4. **Input Validation:**
   All inputs are validated via Pydantic models

## 📱 Mobile Responsiveness

The webapp is fully responsive:
- Tailwind responsive classes (`md:`, `lg:`)
- Touch-friendly buttons and interactions
- Mobile-first design approach

## 🐛 Troubleshooting

### Backend Not Starting
```bash
tail -n 50 /var/log/supervisor/backend.err.log
```

### Frontend Issues
```bash
tail -n 50 /var/log/supervisor/frontend.err.log
```

### Database Connection Issues
```bash
sudo supervisorctl status mongodb
```

### Clear All Data (Reset Database)
```bash
mongosh luvhive_database --eval "db.dropDatabase()"
```

## 📈 Future Enhancements

- [ ] Voice messages in chat
- [ ] Video stories
- [ ] Story reactions
- [ ] User blocking/reporting
- [ ] Advanced search filters
- [ ] Location-based matching
- [ ] Push notifications via Telegram
- [ ] Story highlights (permanent stories)
- [ ] Group chats
- [ ] Video calls integration

## 🤝 Support

For issues or questions:
1. Check logs in `/var/log/supervisor/`
2. Verify environment variables in `.env` files
3. Ensure MongoDB is running
4. Check API responses in browser DevTools

## 📄 License

This project is created for your Telegram bot integration.

---

**Made with ❤️ for LuvHive Social**

🌐 **Live URL:** https://github-repo-view-2.preview.emergentagent.com
