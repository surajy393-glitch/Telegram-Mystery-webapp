from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.environ.get("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    fullName: str
    username: str
    age: int
    gender: str
    password_hash: str
    bio: Optional[str] = ""
    profileImage: Optional[str] = None  # Base64 or file_id
    telegramCode: Optional[str] = None
    telegramUserId: Optional[str] = None
    isPremium: bool = False
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserRegister(BaseModel):
    fullName: str
    username: str
    age: int
    gender: str
    password: str

class UserProfile(BaseModel):
    fullName: str
    username: str
    age: int
    gender: str
    bio: Optional[str] = ""
    profileImage: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Story(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    username: str
    userProfileImage: Optional[str] = None
    mediaType: str  # "image" or "video"
    mediaUrl: str  # Base64 or file_id
    caption: Optional[str] = ""
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expiresAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24))

class StoryCreate(BaseModel):
    mediaType: str
    mediaUrl: str
    caption: Optional[str] = ""

class Post(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    username: str
    userProfileImage: Optional[str] = None
    mediaType: str  # "image" or "video"
    mediaUrl: str  # Base64 or file_id
    caption: Optional[str] = ""
    likes: List[str] = []  # List of user IDs
    comments: List[dict] = []
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PostCreate(BaseModel):
    mediaType: str
    mediaUrl: str
    caption: Optional[str] = ""

class TelegramLink(BaseModel):
    code: str
    userId: str
    telegramUserId: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    senderId: str
    receiverId: str
    message: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Helper functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user)

# Authentication Routes
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    # Check if username exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    user = User(
        fullName=user_data.fullName,
        username=user_data.username,
        age=user_data.age,
        gender=user_data.gender,
        password_hash=get_password_hash(user_data.password)
    )
    
    await db.users.insert_one(user.dict())
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "message": "Registration successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "fullName": user.fullName,
            "username": user.username,
            "age": user.age,
            "gender": user.gender,
            "isPremium": user.isPremium
        }
    }

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    user = await db.users.find_one({"username": user_data.username})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user["id"]})
    
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "fullName": user["fullName"],
            "username": user["username"],
            "age": user["age"],
            "gender": user["gender"],
            "bio": user.get("bio", ""),
            "profileImage": user.get("profileImage"),
            "isPremium": user.get("isPremium", False)
        }
    }

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "fullName": current_user.fullName,
        "username": current_user.username,
        "age": current_user.age,
        "gender": current_user.gender,
        "bio": current_user.bio,
        "profileImage": current_user.profileImage,
        "isPremium": current_user.isPremium,
        "telegramLinked": current_user.telegramUserId is not None
    }

@api_router.put("/auth/profile")
async def update_profile(bio: str = Form(None), profileImage: str = Form(None), current_user: User = Depends(get_current_user)):
    update_data = {}
    if bio is not None:
        update_data["bio"] = bio
    if profileImage is not None:
        update_data["profileImage"] = profileImage
    
    if update_data:
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": update_data}
        )
    
    return {"message": "Profile updated successfully"}

# Telegram Linking
@api_router.post("/telegram/link")
async def link_telegram(code: str, current_user: User = Depends(get_current_user)):
    # In real implementation, verify code with your Telegram bot
    # For now, we'll simulate it
    telegram_link = await db.telegram_links.find_one({"code": code})
    
    if not telegram_link:
        raise HTTPException(status_code=404, detail="Invalid code")
    
    # Update user with telegram info
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"telegramUserId": telegram_link["telegramUserId"], "telegramCode": code}}
    )
    
    return {"message": "Telegram linked successfully"}

# Stories Routes
@api_router.post("/stories/create")
async def create_story(story_data: StoryCreate, current_user: User = Depends(get_current_user)):
    story = Story(
        userId=current_user.id,
        username=current_user.username,
        userProfileImage=current_user.profileImage,
        mediaType=story_data.mediaType,
        mediaUrl=story_data.mediaUrl,
        caption=story_data.caption
    )
    
    await db.stories.insert_one(story.dict())
    
    return {"message": "Story created successfully", "story": story.dict()}

@api_router.get("/stories/feed")
async def get_stories_feed(current_user: User = Depends(get_current_user)):
    # Get all stories that haven't expired
    now = datetime.now(timezone.utc)
    stories = await db.stories.find({"expiresAt": {"$gt": now}}).sort("createdAt", -1).to_list(1000)
    
    # Group stories by user
    stories_by_user = {}
    for story in stories:
        user_id = story["userId"]
        if user_id not in stories_by_user:
            stories_by_user[user_id] = {
                "userId": user_id,
                "username": story["username"],
                "userProfileImage": story.get("userProfileImage"),
                "stories": []
            }
        stories_by_user[user_id]["stories"].append({
            "id": story["id"],
            "mediaType": story["mediaType"],
            "mediaUrl": story["mediaUrl"],
            "caption": story.get("caption", ""),
            "createdAt": story["createdAt"].isoformat()
        })
    
    return {"stories": list(stories_by_user.values())}

# Posts Routes
@api_router.post("/posts/create")
async def create_post(post_data: PostCreate, current_user: User = Depends(get_current_user)):
    post = Post(
        userId=current_user.id,
        username=current_user.username,
        userProfileImage=current_user.profileImage,
        mediaType=post_data.mediaType,
        mediaUrl=post_data.mediaUrl,
        caption=post_data.caption
    )
    
    await db.posts.insert_one(post.dict())
    
    return {"message": "Post created successfully", "post": post.dict()}

@api_router.get("/posts/feed")
async def get_posts_feed(current_user: User = Depends(get_current_user)):
    posts = await db.posts.find().sort("createdAt", -1).to_list(1000)
    
    posts_list = []
    for post in posts:
        posts_list.append({
            "id": post["id"],
            "userId": post["userId"],
            "username": post["username"],
            "userProfileImage": post.get("userProfileImage"),
            "mediaType": post["mediaType"],
            "mediaUrl": post["mediaUrl"],
            "caption": post.get("caption", ""),
            "likes": post.get("likes", []),
            "comments": post.get("comments", []),
            "createdAt": post["createdAt"].isoformat(),
            "isLiked": current_user.id in post.get("likes", [])
        })
    
    return {"posts": posts_list}

@api_router.post("/posts/{post_id}/like")
async def like_post(post_id: str, current_user: User = Depends(get_current_user)):
    post = await db.posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    likes = post.get("likes", [])
    if current_user.id in likes:
        likes.remove(current_user.id)
    else:
        likes.append(current_user.id)
    
    await db.posts.update_one(
        {"id": post_id},
        {"$set": {"likes": likes}}
    )
    
    return {"message": "Success", "likes": len(likes)}

# Chat Routes
@api_router.post("/chat/send")
async def send_message(receiverId: str, message: str, current_user: User = Depends(get_current_user)):
    # Check if sender has premium
    if not current_user.isPremium:
        raise HTTPException(status_code=403, detail="Premium required to send messages")
    
    chat_message = ChatMessage(
        senderId=current_user.id,
        receiverId=receiverId,
        message=message
    )
    
    await db.messages.insert_one(chat_message.dict())
    
    return {"message": "Message sent successfully"}

@api_router.get("/chat/messages/{userId}")
async def get_messages(userId: str, current_user: User = Depends(get_current_user)):
    # Get messages between current user and specified user
    messages = await db.messages.find({
        "$or": [
            {"senderId": current_user.id, "receiverId": userId},
            {"senderId": userId, "receiverId": current_user.id}
        ]
    }).sort("createdAt", 1).to_list(1000)
    
    messages_list = []
    for msg in messages:
        messages_list.append({
            "id": msg["id"],
            "senderId": msg["senderId"],
            "receiverId": msg["receiverId"],
            "message": msg["message"],
            "createdAt": msg["createdAt"].isoformat()
        })
    
    return {"messages": messages_list}

@api_router.get("/users/list")
async def get_users(current_user: User = Depends(get_current_user)):
    users = await db.users.find({"id": {"$ne": current_user.id}}).to_list(1000)
    
    users_list = []
    for user in users:
        users_list.append({
            "id": user["id"],
            "username": user["username"],
            "fullName": user["fullName"],
            "profileImage": user.get("profileImage"),
            "bio": user.get("bio", "")
        })
    
    return {"users": users_list}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()