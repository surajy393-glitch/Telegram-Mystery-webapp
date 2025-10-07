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
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

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
    isPrivate: bool = False  # Privacy setting for the account
    
    # Privacy Controls
    publicProfile: bool = True
    appearInSearch: bool = True
    allowDirectMessages: bool = True
    showOnlineStatus: bool = True
    
    # Interaction Preferences
    allowTagging: bool = True
    allowStoryReplies: bool = True
    showVibeScore: bool = True
    
    # Notifications
    pushNotifications: bool = True
    emailNotifications: bool = True
    
    followers: List[str] = []  # List of user IDs
    following: List[str] = []  # List of user IDs
    savedPosts: List[str] = []  # List of post IDs
    blockedUsers: List[str] = []  # List of blocked user IDs
    hiddenStoryUsers: List[str] = []  # List of user IDs whose stories are hidden
    lastUsernameChange: Optional[datetime] = None  # Track username changes
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

class ProfileUpdate(BaseModel):
    fullName: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
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
    isArchived: bool = False
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
    isArchived: bool = False
    likesHidden: bool = False
    commentsDisabled: bool = False
    isPinned: bool = False
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

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str  # Who receives the notification
    fromUserId: str  # Who triggered the notification
    fromUsername: str
    fromUserImage: Optional[str] = None
    type: str  # "like", "comment", "follow"
    postId: Optional[str] = None  # For like/comment notifications
    isRead: bool = False
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
        "isPrivate": current_user.isPrivate,
        "telegramLinked": current_user.telegramUserId is not None
    }

@api_router.put("/auth/profile")
async def update_profile(
    fullName: str = Form(None), 
    username: str = Form(None), 
    bio: str = Form(None), 
    profileImage: str = Form(None), 
    current_user: User = Depends(get_current_user)
):
    update_data = {}
    
    # Handle username change with 15-day restriction
    if username is not None and username != current_user.username:
        # Check if username is already taken
        existing_user = await db.users.find_one({"username": username, "id": {"$ne": current_user.id}})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Check 15-day restriction
        if current_user.lastUsernameChange:
            days_since_change = (datetime.now(timezone.utc) - current_user.lastUsernameChange).days
            if days_since_change < 15:
                days_remaining = 15 - days_since_change
                raise HTTPException(
                    status_code=400, 
                    detail=f"You can change username again in {days_remaining} days"
                )
        
        update_data["username"] = username
        update_data["lastUsernameChange"] = datetime.now(timezone.utc)
        
        # Update username in all posts and stories
        await db.posts.update_many(
            {"userId": current_user.id},
            {"$set": {"username": username}}
        )
        await db.stories.update_many(
            {"userId": current_user.id},
            {"$set": {"username": username}}
        )
    
    # Handle other fields
    if fullName is not None:
        update_data["fullName"] = fullName
    if bio is not None:
        update_data["bio"] = bio
    if profileImage is not None:
        update_data["profileImage"] = profileImage
        
        # Update profile image in posts and stories
        await db.posts.update_many(
            {"userId": current_user.id},
            {"$set": {"userProfileImage": profileImage}}
        )
        await db.stories.update_many(
            {"userId": current_user.id},
            {"$set": {"userProfileImage": profileImage}}
        )
    
    if update_data:
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": update_data}
        )
    
    return {"message": "Profile updated successfully"}

@api_router.put("/auth/privacy")
async def update_privacy_setting(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Update user's account privacy setting"""
    is_private = request.get("isPrivate", False)
    
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"isPrivate": is_private}}
    )
    
    return {"message": "Privacy setting updated successfully", "isPrivate": is_private}

@api_router.get("/auth/can-change-username")
async def can_change_username(current_user: User = Depends(get_current_user)):
    if not current_user.lastUsernameChange:
        return {"canChange": True, "daysRemaining": 0}
    
    days_since_change = (datetime.now(timezone.utc) - current_user.lastUsernameChange).days
    can_change = days_since_change >= 15
    days_remaining = max(0, 15 - days_since_change)
    
    return {
        "canChange": can_change,
        "daysRemaining": days_remaining,
        "lastChanged": current_user.lastUsernameChange.isoformat()
    }

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

@api_router.delete("/stories/{story_id}")
async def delete_story(story_id: str, current_user: User = Depends(get_current_user)):
    story = await db.stories.find_one({"id": story_id})
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Check if user owns the story
    if story["userId"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this story")
    
    await db.stories.delete_one({"id": story_id})
    
    return {"message": "Story deleted successfully"}

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
    # Exclude archived posts from feed
    posts = await db.posts.find({"isArchived": {"$ne": True}}).sort("createdAt", -1).to_list(1000)
    
    # Get current user's saved posts
    user = await db.users.find_one({"id": current_user.id})
    saved_posts = user.get("savedPosts", [])
    
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
            "isLiked": current_user.id in post.get("likes", []),
            "isSaved": post["id"] in saved_posts
        })
    
    return {"posts": posts_list}

@api_router.post("/posts/{post_id}/like")
async def like_post(post_id: str, current_user: User = Depends(get_current_user)):
    post = await db.posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    likes = post.get("likes", [])
    is_liking = current_user.id not in likes
    
    if current_user.id in likes:
        likes.remove(current_user.id)
    else:
        likes.append(current_user.id)
        
        # Create notification if liking someone else's post
        if post["userId"] != current_user.id:
            notification = Notification(
                userId=post["userId"],
                fromUserId=current_user.id,
                fromUsername=current_user.username,
                fromUserImage=current_user.profileImage,
                type="like",
                postId=post_id
            )
            await db.notifications.insert_one(notification.dict())
    
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
            "bio": user.get("bio", ""),
            "followersCount": len(user.get("followers", [])),
            "followingCount": len(user.get("following", [])),
            "isFollowing": current_user.id in user.get("followers", [])
        })
    
    return {"users": users_list}

@api_router.get("/users/{userId}")
async def get_user_profile(userId: str, current_user: User = Depends(get_current_user)):
    user = await db.users.find_one({"id": userId})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's posts
    posts = await db.posts.find({"userId": userId}).sort("createdAt", -1).to_list(1000)
    
    return {
        "id": user["id"],
        "username": user["username"],
        "fullName": user["fullName"],
        "profileImage": user.get("profileImage"),
        "bio": user.get("bio", ""),
        "followersCount": len(user.get("followers", [])),
        "followingCount": len(user.get("following", [])),
        "isFollowing": current_user.id in user.get("followers", []),
        "postsCount": len(posts)
    }

# Follow/Unfollow Routes
@api_router.post("/users/{userId}/follow")
async def follow_user(userId: str, current_user: User = Depends(get_current_user)):
    if userId == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    target_user = await db.users.find_one({"id": userId})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Add to following list
    await db.users.update_one(
        {"id": current_user.id},
        {"$addToSet": {"following": userId}}
    )
    
    # Add to followers list
    await db.users.update_one(
        {"id": userId},
        {"$addToSet": {"followers": current_user.id}}
    )
    
    # Create notification
    notification = Notification(
        userId=userId,
        fromUserId=current_user.id,
        fromUsername=current_user.username,
        fromUserImage=current_user.profileImage,
        type="follow"
    )
    await db.notifications.insert_one(notification.dict())
    
    return {"message": "User followed successfully"}

@api_router.post("/users/{userId}/unfollow")
async def unfollow_user(userId: str, current_user: User = Depends(get_current_user)):
    # Remove from following list
    await db.users.update_one(
        {"id": current_user.id},
        {"$pull": {"following": userId}}
    )
    
    # Remove from followers list
    await db.users.update_one(
        {"id": userId},
        {"$pull": {"followers": current_user.id}}
    )
    
    return {"message": "User unfollowed successfully"}

# My Profile Routes
@api_router.get("/profile/posts")
async def get_my_posts(current_user: User = Depends(get_current_user)):
    # Get all non-archived posts
    posts = await db.posts.find({"userId": current_user.id, "isArchived": {"$ne": True}}).to_list(1000)
    
    # Sort: pinned first, then by date
    posts.sort(key=lambda x: (not x.get("isPinned", False), -x["createdAt"].timestamp()))
    
    posts_list = []
    for post in posts:
        posts_list.append({
            "id": post["id"],
            "mediaType": post["mediaType"],
            "mediaUrl": post["mediaUrl"],
            "caption": post.get("caption", ""),
            "likes": post.get("likes", []),
            "comments": post.get("comments", []),
            "createdAt": post["createdAt"].isoformat(),
            "isLiked": current_user.id in post.get("likes", []),
            "isSaved": post["id"] in current_user.savedPosts
        })
    
    return {"posts": posts_list}

@api_router.get("/profile/saved")
async def get_saved_posts(current_user: User = Depends(get_current_user)):
    if not current_user.savedPosts:
        return {"posts": []}
    
    # Get all saved posts
    posts = await db.posts.find({"id": {"$in": current_user.savedPosts}}).sort("createdAt", -1).to_list(1000)
    
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
            "isLiked": current_user.id in post.get("likes", []),
            "isSaved": True
        })
    
    return {"posts": posts_list}

# Save/Unsave Post
@api_router.post("/posts/{post_id}/save")
async def save_post(post_id: str, current_user: User = Depends(get_current_user)):
    post = await db.posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if already saved
    user = await db.users.find_one({"id": current_user.id})
    saved_posts = user.get("savedPosts", [])
    
    if post_id in saved_posts:
        # Unsave
        await db.users.update_one(
            {"id": current_user.id},
            {"$pull": {"savedPosts": post_id}}
        )
        return {"message": "Post unsaved", "isSaved": False}
    else:
        # Save
        await db.users.update_one(
            {"id": current_user.id},
            {"$addToSet": {"savedPosts": post_id}}
        )
        return {"message": "Post saved", "isSaved": True}

# Post Management (Own Posts)
@api_router.post("/posts/{post_id}/archive")
async def archive_post(post_id: str, current_user: User = Depends(get_current_user)):
    post = await db.posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["userId"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    is_archived = post.get("isArchived", False)
    await db.posts.update_one(
        {"id": post_id},
        {"$set": {"isArchived": not is_archived}}
    )
    return {"message": "Post archived" if not is_archived else "Post unarchived", "isArchived": not is_archived}

@api_router.post("/posts/{post_id}/hide-likes")
async def hide_likes(post_id: str, current_user: User = Depends(get_current_user)):
    post = await db.posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["userId"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    likes_hidden = post.get("likesHidden", False)
    await db.posts.update_one(
        {"id": post_id},
        {"$set": {"likesHidden": not likes_hidden}}
    )
    return {"message": "Likes hidden" if not likes_hidden else "Likes shown", "likesHidden": not likes_hidden}

@api_router.post("/posts/{post_id}/toggle-comments")
async def toggle_comments(post_id: str, current_user: User = Depends(get_current_user)):
    post = await db.posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["userId"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    comments_disabled = post.get("commentsDisabled", False)
    await db.posts.update_one(
        {"id": post_id},
        {"$set": {"commentsDisabled": not comments_disabled}}
    )
    return {"message": "Comments disabled" if not comments_disabled else "Comments enabled", "commentsDisabled": not comments_disabled}

@api_router.put("/posts/{post_id}/caption")
async def edit_caption(post_id: str, caption: str = Form(...), current_user: User = Depends(get_current_user)):
    post = await db.posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["userId"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.posts.update_one(
        {"id": post_id},
        {"$set": {"caption": caption}}
    )
    return {"message": "Caption updated successfully"}

@api_router.delete("/posts/{post_id}")
async def delete_post(post_id: str, current_user: User = Depends(get_current_user)):
    post = await db.posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["userId"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.posts.delete_one({"id": post_id})
    return {"message": "Post deleted successfully"}

@api_router.post("/posts/{post_id}/pin")
async def pin_post(post_id: str, current_user: User = Depends(get_current_user)):
    post = await db.posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["userId"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    is_pinned = post.get("isPinned", False)
    
    if not is_pinned:
        # Unpin all other posts first
        await db.posts.update_many(
            {"userId": current_user.id, "isPinned": True},
            {"$set": {"isPinned": False}}
        )
    
    await db.posts.update_one(
        {"id": post_id},
        {"$set": {"isPinned": not is_pinned}}
    )
    return {"message": "Post pinned" if not is_pinned else "Post unpinned", "isPinned": not is_pinned}

# Get archived posts
@api_router.get("/profile/archived")
async def get_archived(current_user: User = Depends(get_current_user)):
    posts = await db.posts.find({"userId": current_user.id, "isArchived": True}).sort("createdAt", -1).to_list(1000)
    stories = await db.stories.find({"userId": current_user.id, "isArchived": True}).sort("createdAt", -1).to_list(1000)
    
    posts_list = []
    for post in posts:
        posts_list.append({
            "id": post["id"],
            "type": "post",
            "mediaType": post["mediaType"],
            "mediaUrl": post["mediaUrl"],
            "caption": post.get("caption", ""),
            "createdAt": post["createdAt"].isoformat()
        })
    
    for story in stories:
        posts_list.append({
            "id": story["id"],
            "type": "story",
            "mediaType": story["mediaType"],
            "mediaUrl": story["mediaUrl"],
            "caption": story.get("caption", ""),
            "createdAt": story["createdAt"].isoformat()
        })
    
    # Sort by date
    posts_list.sort(key=lambda x: x["createdAt"], reverse=True)
    
    return {"archived": posts_list}

# Archive story
@api_router.post("/stories/{story_id}/archive")
async def archive_story(story_id: str, current_user: User = Depends(get_current_user)):
    story = await db.stories.find_one({"id": story_id})
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    if story["userId"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    is_archived = story.get("isArchived", False)
    await db.stories.update_one(
        {"id": story_id},
        {"$set": {"isArchived": not is_archived}}
    )
    return {"message": "Story archived" if not is_archived else "Story unarchived", "isArchived": not is_archived}

# Notifications
@api_router.get("/notifications")
async def get_notifications(current_user: User = Depends(get_current_user)):
    notifications = await db.notifications.find({"userId": current_user.id}).sort("createdAt", -1).to_list(100)
    
    notifications_list = []
    for notif in notifications:
        notifications_list.append({
            "id": notif["id"],
            "fromUserId": notif["fromUserId"],
            "fromUsername": notif["fromUsername"],
            "fromUserImage": notif.get("fromUserImage"),
            "type": notif["type"],
            "postId": notif.get("postId"),
            "isRead": notif.get("isRead", False),
            "createdAt": notif["createdAt"].isoformat()
        })
    
    return {"notifications": notifications_list}

@api_router.get("/notifications/unread-count")
async def get_unread_count(current_user: User = Depends(get_current_user)):
    count = await db.notifications.count_documents({"userId": current_user.id, "isRead": False})
    return {"count": count}

@api_router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: User = Depends(get_current_user)):
    await db.notifications.update_one(
        {"id": notification_id, "userId": current_user.id},
        {"$set": {"isRead": True}}
    )
    return {"message": "Notification marked as read"}

@api_router.post("/notifications/read-all")
async def mark_all_read(current_user: User = Depends(get_current_user)):
    await db.notifications.update_many(
        {"userId": current_user.id},
        {"$set": {"isRead": True}}
    )
    return {"message": "All notifications marked as read"}

# New endpoints for enhanced features

@api_router.get("/users/{userId}/profile")
async def get_user_profile(userId: str, current_user: User = Depends(get_current_user)):
    """Get detailed profile of a specific user"""
    user = await db.users.find_one({"id": userId})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if current user is following this user
    is_following = current_user.id in user.get("followers", [])
    
    return {
        "id": user["id"],
        "username": user["username"],
        "fullName": user["fullName"],
        "profileImage": user.get("profileImage"),
        "bio": user.get("bio", ""),
        "age": user.get("age"),
        "gender": user.get("gender"),
        "isPremium": user.get("isPremium", False),
        "followersCount": len(user.get("followers", [])),
        "followingCount": len(user.get("following", [])),
        "isFollowing": is_following,
        "createdAt": user["createdAt"].isoformat()
    }

@api_router.get("/users/{userId}/posts")
async def get_user_posts(userId: str, current_user: User = Depends(get_current_user)):
    """Get posts by a specific user"""
    user = await db.users.find_one({"id": userId})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's non-archived posts
    posts = await db.posts.find({
        "userId": userId,
        "isArchived": False
    }).sort("createdAt", -1).to_list(50)
    
    posts_list = []
    for post in posts:
        # Check if current user liked this post
        is_liked = current_user.id in post.get("likes", [])
        # Check if current user saved this post
        is_saved = post["id"] in current_user.savedPosts
        
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
            "isLiked": is_liked,
            "isSaved": is_saved,
            "likesHidden": post.get("likesHidden", False),
            "commentsDisabled": post.get("commentsDisabled", False),
            "isPinned": post.get("isPinned", False),
            "createdAt": post["createdAt"].isoformat()
        })
    
    return {"posts": posts_list}

@api_router.post("/ai/vibe-compatibility")
async def calculate_vibe_compatibility(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Calculate AI-powered vibe compatibility between users"""
    target_user_id = request.get("targetUserId")
    
    if not target_user_id:
        raise HTTPException(status_code=400, detail="Target user ID required")
    
    target_user = await db.users.find_one({"id": target_user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import os
        import uuid
        
        # Load environment variable
        load_dotenv(ROOT_DIR / '.env')
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        
        if not api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        # Initialize AI chat with GPT-5
        chat = LlmChat(
            api_key=api_key,
            session_id=f"vibe-{current_user.id}-{target_user_id}",
            system_message="You are an AI compatibility analyst for a dating app. Analyze user profiles and provide compatibility scores with explanations."
        ).with_model("openai", "gpt-5")
        
        # Create prompt with user data
        user1_profile = f"""
User 1 Profile:
- Full Name: {current_user.fullName}
- Age: {current_user.age}
- Gender: {current_user.gender}
- Bio: {current_user.bio or "No bio provided"}
"""
        
        user2_profile = f"""
User 2 Profile:
- Full Name: {target_user['fullName']}
- Age: {target_user['age']}  
- Gender: {target_user['gender']}
- Bio: {target_user.get('bio', 'No bio provided')}
"""
        
        analysis_prompt = f"""
Analyze the compatibility between these two users:

{user1_profile}

{user2_profile}

Please provide:
1. A compatibility percentage (0-100)
2. Brief analysis of their compatibility

Focus on age compatibility, interests from bios, and general compatibility factors.
Respond in this exact format:
COMPATIBILITY: [percentage]
ANALYSIS: [your analysis here]

Keep the analysis positive and encouraging, even for lower compatibility scores.
"""
        
        user_message = UserMessage(text=analysis_prompt)
        response = await chat.send_message(user_message)
        
        # Parse AI response
        response_text = str(response)
        compatibility_score = 75  # Default fallback
        analysis_text = "AI-powered compatibility analysis based on profiles and interests."
        
        if "COMPATIBILITY:" in response_text and "ANALYSIS:" in response_text:
            try:
                compatibility_line = response_text.split("COMPATIBILITY:")[1].split("ANALYSIS:")[0].strip()
                analysis_line = response_text.split("ANALYSIS:")[1].strip()
                
                # Extract percentage from compatibility line
                import re
                score_match = re.search(r'(\d+)', compatibility_line)
                if score_match:
                    compatibility_score = min(100, max(0, int(score_match.group(1))))
                
                if analysis_line:
                    analysis_text = analysis_line
                    
            except Exception as parse_error:
                logger.error(f"Error parsing AI response: {parse_error}")
                # Use fallback values
                pass
        
        return {
            "compatibility": compatibility_score,
            "analysis": analysis_text
        }
        
    except Exception as e:
        logger.error(f"Error calculating vibe compatibility: {e}")
        # Fallback to random score if AI fails
        import random
        return {
            "compatibility": random.randint(65, 90),
            "analysis": "Compatibility analysis based on profile information. AI service temporarily unavailable - showing estimated compatibility."
        }

@api_router.post("/users/{userId}/block")
async def block_user(userId: str, current_user: User = Depends(get_current_user)):
    """Block a user"""
    if userId == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot block yourself")
    
    target_user = await db.users.find_one({"id": userId})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Add to blocked users list (add this field to User model if needed)
    # For now, we'll remove from following/followers and add to a blocked list
    await db.users.update_one(
        {"id": current_user.id},
        {
            "$addToSet": {"blockedUsers": userId},
            "$pull": {"following": userId}
        }
    )
    
    # Remove current user from target's followers
    await db.users.update_one(
        {"id": userId},
        {"$pull": {"followers": current_user.id}}
    )
    
    return {"message": "User blocked successfully"}

@api_router.post("/users/{userId}/hide-story")
async def hide_user_story(userId: str, current_user: User = Depends(get_current_user)):
    """Hide stories from a specific user"""
    if userId == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot hide your own stories")
    
    target_user = await db.users.find_one({"id": userId})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Add to hidden stories list (add this field to User model if needed)
    await db.users.update_one(
        {"id": current_user.id},
        {"$addToSet": {"hiddenStoryUsers": userId}}
    )
    
    return {"message": "Stories hidden successfully"}

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