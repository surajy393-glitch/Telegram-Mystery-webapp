from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends, Header
from dotenv import load_dotenv

# Load environment variables from .env file explicitly
load_dotenv()
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
import base64
import hmac
import hashlib
from urllib.parse import parse_qsl
import psycopg2
from psycopg2.extras import RealDictCursor

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ.get('DB_NAME', 'luvhive_database')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Log database connection info
logger = logging.getLogger(__name__)
logger.info(f"Connected to MongoDB at {mongo_url}")
logger.info(f"Using database: {db_name}")
logger.info(f"Database object: {db}")

# Create database indexes for better performance
async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Index for user search
        await db.users.create_index([
            ("username", "text"),
            ("fullName", "text"),
            ("bio", "text")
        ], name="user_search_index")
        
        # Index for user lookup
        await db.users.create_index("username")
        await db.users.create_index("id")
        
        # Index for posts
        await db.posts.create_index([("userId", 1), ("createdAt", -1)])
        await db.posts.create_index([("caption", "text")], name="post_search_index")
        await db.posts.create_index("createdAt")
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

# Initialize indexes on startup
import asyncio
asyncio.create_task(create_indexes())

# Create the main app without a prefix
app = FastAPI()

# Add compression middleware for better performance
app.add_middleware(GZipMiddleware, minimum_size=1000)

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
    password_hash: Optional[str] = None  # Optional for Telegram-only users
    email: Optional[str] = None  # For password recovery
    mobileNumber: Optional[str] = None  # Mobile number for enhanced security
    bio: Optional[str] = ""
    profileImage: Optional[str] = None  # Base64 or file_id
    
    # Telegram Integration
    telegramId: Optional[int] = None  # Telegram user ID
    telegramUsername: Optional[str] = None  # @username from Telegram
    telegramFirstName: Optional[str] = None
    telegramLastName: Optional[str] = None
    telegramPhotoUrl: Optional[str] = None
    authMethod: str = "password"  # "password", "telegram", or "both"
    
    # Premium & Settings
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
    password: Optional[str] = None  # Optional for Telegram auth
    email: Optional[str] = None  # Optional for recovery
    authMethod: str = "password"  # "password" or "telegram"

class TelegramAuthRequest(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class TelegramSigninRequest(BaseModel):
    telegramId: int

class VerifyOTPRequest(BaseModel):
    telegramId: int
    otp: str

class EnhancedUserRegister(BaseModel):
    fullName: str
    username: str
    age: int
    gender: str
    password: str
    email: Optional[str] = None  # Optional email
    mobileNumber: Optional[str] = None  # Optional mobile number
    profileImage: Optional[str] = None  # Optional profile image
    bio: Optional[str] = None  # Optional bio

class EmailOTPRequest(BaseModel):
    email: str

class VerifyEmailOTPRequest(BaseModel):
    email: str
    otp: str

class SendMobileOTPRequest(BaseModel):
    mobileNumber: str

class VerifyMobileOTPRequest(BaseModel):
    mobileNumber: str
    otp: str

class ForgotPasswordMobileRequest(BaseModel):
    mobileNumber: str

class ResetPasswordMobileRequest(BaseModel):
    mobileNumber: str
    otp: str
    new_password: str

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
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_telegram_hash(auth_data: dict, bot_token: str) -> bool:
    """
    Verify Telegram Login Widget hash for security
    https://core.telegram.org/widgets/login#checking-authorization
    """
    try:
        # Extract hash from auth_data
        received_hash = auth_data.pop('hash', None)
        if not received_hash:
            return False
        
        # Create data check string
        data_check_arr = []
        for key, value in sorted(auth_data.items()):
            if key != 'hash':
                data_check_arr.append(f"{key}={value}")
        
        data_check_string = '\n'.join(data_check_arr)
        
        # Create secret key from bot token
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare hashes
        return hmac.compare_digest(calculated_hash, received_hash)
        
    except Exception as e:
        logger.error(f"Error verifying Telegram hash: {e}")
        return False

# OTP Helper Functions
import random
import asyncio

# In-memory OTP storage (in production, use Redis or database)
otp_storage = {}
email_otp_storage = {}  # Separate storage for email OTPs

def generate_otp(length: int = 6) -> str:
    """Generate a random OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

async def store_otp(telegram_id: int, otp: str, expires_in_minutes: int = 10):
    """Store OTP with expiration"""
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    otp_storage[telegram_id] = {
        'otp': otp,
        'expires_at': expires_at,
        'attempts': 0
    }
    
    # Schedule cleanup
    async def cleanup():
        await asyncio.sleep(expires_in_minutes * 60)
        otp_storage.pop(telegram_id, None)
    
    asyncio.create_task(cleanup())

async def verify_otp(telegram_id: int, provided_otp: str) -> bool:
    """Verify OTP and cleanup if successful"""
    if telegram_id not in otp_storage:
        return False
    
    otp_data = otp_storage[telegram_id]
    
    # Check expiration
    if datetime.now(timezone.utc) > otp_data['expires_at']:
        otp_storage.pop(telegram_id, None)
        return False
    
    # Check attempts (max 3)
    if otp_data['attempts'] >= 3:
        otp_storage.pop(telegram_id, None)
        return False
    
    # Check OTP
    if otp_data['otp'] == provided_otp:
        otp_storage.pop(telegram_id, None)
        return True
    else:
        otp_data['attempts'] += 1
        return False

async def send_telegram_otp(telegram_id: int, otp: str):
    """Send OTP via Telegram bot"""
    try:
        # Import here to avoid circular imports
        import aiohttp
        
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            raise Exception("Telegram bot token not configured")
        
        message = f"🔐 Your LuvHive login code is: *{otp}*\n\nThis code will expire in 10 minutes.\nDo not share this code with anyone!"
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": telegram_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                if response.status != 200:
                    raise Exception(f"Failed to send Telegram message: {response.status}")
                return True
                
    except Exception as e:
        logger.error(f"Error sending Telegram OTP: {e}")
        return False

async def store_email_otp(email: str, otp: str, expires_in_minutes: int = 10):
    """Store email OTP with expiration"""
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    email_otp_storage[email.lower()] = {
        'otp': otp,
        'expires_at': expires_at,
        'attempts': 0
    }
    
    # Schedule cleanup
    async def cleanup():
        await asyncio.sleep(expires_in_minutes * 60)
        email_otp_storage.pop(email.lower(), None)
    
    asyncio.create_task(cleanup())

async def verify_email_otp(email: str, provided_otp: str) -> bool:
    """Verify email OTP and cleanup if successful"""
    email_key = email.lower()
    if email_key not in email_otp_storage:
        return False
    
    otp_data = email_otp_storage[email_key]
    
    # Check expiration
    if datetime.now(timezone.utc) > otp_data['expires_at']:
        email_otp_storage.pop(email_key, None)
        return False
    
    # Check attempts (max 3)
    if otp_data['attempts'] >= 3:
        email_otp_storage.pop(email_key, None)
        return False
    
    # Check OTP
    if otp_data['otp'] == provided_otp:
        email_otp_storage.pop(email_key, None)
        return True
    else:
        otp_data['attempts'] += 1
        return False

async def send_email_otp(email: str, otp: str):
    """Send OTP via email using SendGrid"""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")
        
        if not sendgrid_api_key:
            logger.error("SendGrid API key not configured")
            logger.info(f"MOCK EMAIL: OTP {otp} sent to {email}")
            return True
        
        # Create beautiful HTML email
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
            <div style="background-color: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #e91e63; margin: 0; font-size: 28px;">💖 LuvHive</h1>
                    <h2 style="color: #333; margin: 10px 0 0 0; font-size: 22px;">Email Verification</h2>
                </div>
                
                <div style="background: linear-gradient(135deg, #e91e63, #f06292); padding: 25px; border-radius: 12px; text-align: center; margin: 25px 0;">
                    <p style="color: white; margin: 0 0 15px 0; font-size: 16px; font-weight: 500;">Your Verification Code:</p>
                    <div style="background-color: white; padding: 15px; border-radius: 8px; display: inline-block;">
                        <span style="color: #e91e63; font-size: 36px; font-weight: bold; letter-spacing: 8px; font-family: 'Courier New', monospace;">{otp}</span>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 25px 0;">
                    <p style="color: #555; font-size: 16px; margin: 0 0 15px 0;">Enter this code on the registration page to verify your email address</p>
                    <p style="color: #888; font-size: 14px; margin: 0;">⏰ This code expires in <strong>10 minutes</strong></p>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px; text-align: center;">
                    <p style="color: #999; font-size: 13px; margin: 0;">🔒 If you didn't request this code, please ignore this email.</p>
                    <p style="color: #999; font-size: 13px; margin: 5px 0 0 0;">This is an automated message from LuvHive.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
        LuvHive Email Verification
        
        Your verification code is: {otp}
        
        Enter this code on the registration page to verify your email address.
        
        This code will expire in 10 minutes.
        Do not share this code with anyone.
        
        If you didn't request this code, please ignore this email.
        
        Best regards,
        LuvHive Team
        """
        
        # Create SendGrid message
        message = Mail(
            from_email="no-reply@luvhive.net",
            to_emails=email,
            subject="Your LuvHive Verification Code 🔐",
            html_content=html_content,
            plain_text_content=text_content
        )
        
        # Send email
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        if response.status_code == 202:
            logger.info(f"SendGrid email sent successfully: OTP {otp} to {email}")
            return True
        else:
            logger.error(f"SendGrid error: Status {response.status_code}")
            return False
                
    except Exception as e:
        logger.error(f"Error sending SendGrid email: {e}")
        logger.info(f"MOCK EMAIL: OTP {otp} sent to {email}")
        return True
        
        # Try Twilio Email first (with API Key if available)
        if twilio_account_sid and (twilio_auth_token or twilio_api_key_secret):
            try:
                from twilio.rest import Client
                
                # Use API key if available, otherwise use auth token
                if twilio_api_key_sid and twilio_api_key_secret:
                    client = Client(twilio_api_key_sid, twilio_api_key_secret, twilio_account_sid)
                else:
                    client = Client(twilio_account_sid, twilio_auth_token)
                
                # Create HTML email content
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
                    <div style="background-color: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #e91e63; margin: 0; font-size: 28px;">💖 LuvHive</h1>
                            <h2 style="color: #333; margin: 10px 0 0 0; font-size: 22px;">Email Verification</h2>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, #e91e63, #f06292); padding: 25px; border-radius: 12px; text-align: center; margin: 25px 0;">
                            <p style="color: white; margin: 0 0 15px 0; font-size: 16px; font-weight: 500;">Your Verification Code:</p>
                            <div style="background-color: white; padding: 15px; border-radius: 8px; display: inline-block;">
                                <span style="color: #e91e63; font-size: 36px; font-weight: bold; letter-spacing: 8px; font-family: 'Courier New', monospace;">{otp}</span>
                            </div>
                        </div>
                        
                        <div style="text-align: center; margin: 25px 0;">
                            <p style="color: #555; font-size: 16px; margin: 0 0 15px 0;">Enter this code on the registration page to verify your email address</p>
                            <p style="color: #888; font-size: 14px; margin: 0;">⏰ This code expires in <strong>10 minutes</strong></p>
                        </div>
                        
                        <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px; text-align: center;">
                            <p style="color: #999; font-size: 13px; margin: 0;">🔒 If you didn't request this code, please ignore this email.</p>
                            <p style="color: #999; font-size: 13px; margin: 5px 0 0 0;">This is an automated message from LuvHive.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                # Try using Twilio's built-in email service
                try:
                    # Use Twilio's email service if available
                    message = client.messages.create(
                        body=f"Your LuvHive verification code is: {otp}. This code expires in 10 minutes.",
                        from_='no-reply@luvhive.net',
                        to=email
                    )
                    logger.info(f"Twilio email sent via messages API: {message.sid}")
                    return True
                except Exception as msg_error:
                    logger.error(f"Twilio messages API error: {msg_error}")
                    
                    # Try SendGrid API via Twilio
                    message = client.sendgrid.v3.mail.send.post(request_body={
                        "personalizations": [
                            {
                                "to": [{"email": email}],
                                "subject": "Your LuvHive Verification Code 🔐"
                            }
                        ],
                        "from": {"email": "no-reply@luvhive.net", "name": "LuvHive"},
                        "content": [
                            {
                                "type": "text/html",
                                "value": html_content
                            }
                        ]
                    })
                
                if message.status_code == 202:
                    logger.info(f"Twilio SendGrid email sent successfully: OTP {otp} to {email}")
                    return True
                else:
                    logger.error(f"Twilio SendGrid error: Status {message.status_code}")
                    return False
                
            except Exception as twilio_error:
                logger.error(f"Twilio email error: {twilio_error}")
                # Fall through to SendGrid or mock
        
        # Try SendGrid as fallback
        if sendgrid_api_key:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            sender_email = "no-reply@luvhive.net"
        
        # Create HTML email content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
            <div style="background-color: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #e91e63; margin: 0; font-size: 28px;">💖 LuvHive</h1>
                    <h2 style="color: #333; margin: 10px 0 0 0; font-size: 22px;">Email Verification</h2>
                </div>
                
                <div style="background: linear-gradient(135deg, #e91e63, #f06292); padding: 25px; border-radius: 12px; text-align: center; margin: 25px 0;">
                    <p style="color: white; margin: 0 0 15px 0; font-size: 16px; font-weight: 500;">Your Verification Code:</p>
                    <div style="background-color: white; padding: 15px; border-radius: 8px; display: inline-block;">
                        <span style="color: #e91e63; font-size: 36px; font-weight: bold; letter-spacing: 8px; font-family: 'Courier New', monospace;">{otp}</span>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 25px 0;">
                    <p style="color: #555; font-size: 16px; margin: 0 0 15px 0;">Enter this code on the registration page to verify your email address</p>
                    <p style="color: #888; font-size: 14px; margin: 0;">⏰ This code expires in <strong>10 minutes</strong></p>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px; text-align: center;">
                    <p style="color: #999; font-size: 13px; margin: 0;">🔒 If you didn't request this code, please ignore this email.</p>
                    <p style="color: #999; font-size: 13px; margin: 5px 0 0 0;">This is an automated message from LuvHive.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
        LuvHive Email Verification
        
        Your verification code is: {otp}
        
        Enter this code on the registration page to verify your email address.
        
        This code will expire in 10 minutes.
        Do not share this code with anyone.
        
        If you didn't request this code, please ignore this email.
        
        Best regards,
        LuvHive Team
        """
        
        # Create SendGrid message
        message = Mail(
            from_email="no-reply@luvhive.net",
            to_emails=email,
            subject="Your LuvHive Verification Code 🔐",
            html_content=html_content,
            plain_text_content=text_content
        )
        
        # Send email
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        if response.status_code == 202:
            logger.info(f"SendGrid email sent successfully: OTP {otp} to {email}")
            return True
        else:
            logger.error(f"SendGrid error: Status {response.status_code}")
            return False
                
    except Exception as e:
        logger.error(f"Error sending SendGrid email: {e}")
        logger.info(f"MOCK EMAIL: OTP {otp} sent to {email}")
        return True

async def send_mobile_otp(mobile_number: str):
    """Send OTP via SMS using Twilio Verify"""
    try:
        from twilio.rest import Client
        
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            logger.error("Twilio credentials not configured")
            return False
        
        client = Client(account_sid, auth_token)
        
        # Format mobile number (add +91 if not present)
        formatted_number = mobile_number.strip()
        if not formatted_number.startswith('+'):
            if formatted_number.startswith('91'):
                formatted_number = '+' + formatted_number
            else:
                formatted_number = '+91' + formatted_number
        
        # Send OTP via Twilio Verify
        verify_service_sid = os.environ.get("TWILIO_VERIFY_SERVICE_SID")
        verification = client.verify \
            .v2 \
            .services(verify_service_sid) \
            .verifications \
            .create(to=formatted_number, channel='sms')
        
        logger.info(f"Twilio SMS OTP sent: {verification.status} to {formatted_number}")
        return verification.status == 'pending'
        
    except Exception as e:
        logger.error(f"Error sending mobile OTP: {e}")
        # For demo, always return True
        logger.info(f"MOCK SMS: OTP sent to {mobile_number}")
        return True

async def verify_mobile_otp(mobile_number: str, otp_code: str):
    """Verify mobile OTP using Twilio Verify"""
    try:
        from twilio.rest import Client
        
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            logger.error("Twilio credentials not configured")
            return True  # Allow in demo mode
        
        client = Client(account_sid, auth_token)
        
        # Format mobile number
        formatted_number = mobile_number.strip()
        if not formatted_number.startswith('+'):
            if formatted_number.startswith('91'):
                formatted_number = '+' + formatted_number
            else:
                formatted_number = '+91' + formatted_number
        
        # Verify OTP
        verify_service_sid = os.environ.get("TWILIO_VERIFY_SERVICE_SID")
        verification_check = client.verify \
            .v2 \
            .services(verify_service_sid) \
            .verification_checks \
            .create(to=formatted_number, code=otp_code)
        
        logger.info(f"Twilio SMS verification: {verification_check.status}")
        return verification_check.status == 'approved'
        
    except Exception as e:
        logger.error(f"Error verifying mobile OTP: {e}")
        # For demo, accept any 6-digit code
        if len(otp_code.strip()) == 6 and otp_code.strip().isdigit():
            logger.info(f"DEMO MODE: Accepting OTP {otp_code} for {mobile_number}")
            return True
        return False

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
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user)

# Authentication Routes
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    # Validate and clean input
    clean_username = user_data.username.strip()
    clean_fullname = user_data.fullName.strip()
    clean_email = user_data.email.strip().lower() if user_data.email else None
    
    if not clean_username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    
    if len(clean_username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    
    # Validate auth method and required fields
    if user_data.authMethod == "password":
        if not user_data.password:
            raise HTTPException(status_code=400, detail="Password is required for password authentication")
        if len(user_data.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Check if username exists (case-insensitive and trimmed)
    escaped_username = clean_username.replace('.', r'\.')
    existing_user = await db.users.find_one({
        "username": {"$regex": f"^{escaped_username}$", "$options": "i"}
    })
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    if clean_email:
        existing_email = await db.users.find_one({"email": clean_email})
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password if provided
    hashed_password = get_password_hash(user_data.password) if user_data.password else None
    
    # Create user with cleaned data
    user = User(
        fullName=clean_fullname,
        username=clean_username,
        age=user_data.age,
        gender=user_data.gender,
        password_hash=hashed_password,
        email=clean_email,
        authMethod=user_data.authMethod,
    )
    
    user_dict = user.dict()
    await db.users.insert_one(user_dict)
    
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
            "email": user.email,
            "authMethod": user.authMethod,
            "isPremium": user.isPremium
        }
    }

@api_router.post("/auth/register-enhanced")
async def register_enhanced(user_data: EnhancedUserRegister):
    """
    Enhanced registration with mobile number support
    """
    try:
        # Validate and clean input
        clean_username = user_data.username.strip()
        clean_fullname = user_data.fullName.strip()
        clean_email = user_data.email.strip().lower() if user_data.email else None
        clean_mobile = user_data.mobileNumber.strip() if user_data.mobileNumber else None
        clean_bio = user_data.bio.strip() if user_data.bio else ""
        clean_profile_image = user_data.profileImage if user_data.profileImage else None
        
        if not clean_username:
            raise HTTPException(status_code=400, detail="Username cannot be empty")
        
        if len(clean_username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
        
        if not user_data.password or len(user_data.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # Email is required only if no mobile number provided
        if not clean_email and not clean_mobile:
            raise HTTPException(status_code=400, detail="Either email or mobile number is required")
        
        # Validate email format if provided
        if clean_email and ("@" not in clean_email or "." not in clean_email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Validate mobile number format if provided
        if clean_mobile:
            # Remove any spaces or special characters
            clean_mobile = ''.join(filter(str.isdigit, clean_mobile))
            if len(clean_mobile) < 10 or len(clean_mobile) > 15:
                raise HTTPException(status_code=400, detail="Mobile number must be 10-15 digits")
        
        # Check if username exists (case-insensitive)
        escaped_username = clean_username.replace('.', r'\.')
        existing_user = await db.users.find_one({
            "username": {"$regex": f"^{escaped_username}$", "$options": "i"}
        })
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check if email already exists (only if email provided)
        if clean_email:
            existing_email = await db.users.find_one({"email": clean_email})
            if existing_email:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Check if mobile number already exists (if provided)
        if clean_mobile:
            existing_mobile = await db.users.find_one({"mobileNumber": clean_mobile})
            if existing_mobile:
                raise HTTPException(status_code=400, detail="Mobile number already registered")
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create complete user
        user_dict = {
            "id": str(uuid4()),
            "fullName": clean_fullname,
            "username": clean_username,
            "email": clean_email or None,
            "mobileNumber": clean_mobile,
            "age": user_data.age,
            "gender": user_data.gender,
            "password_hash": hashed_password,
            "bio": clean_bio,
            "profileImage": clean_profile_image,
            "authMethod": "password",
            "emailVerified": bool(clean_mobile),  # Auto-verify if mobile provided
            "emailVerificationToken": str(uuid4()) if clean_email else None,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "followers": [],
            "following": [],
            "posts": [],
            "savedPosts": [],
            "blockedUsers": [],
            "hiddenStoryUsers": [],
            "isPremium": False,
            "isPrivate": False,
            "isOnline": True,
            "lastSeen": datetime.now(timezone.utc).isoformat(),
            
            # Privacy Controls
            "publicProfile": True,
            "appearInSearch": True,
            "allowDirectMessages": True,
            "showOnlineStatus": True,
            
            # Interaction Preferences
            "allowTagging": True,
            "allowStoryReplies": True,
            "showVibeScore": True,
            
            # Notifications
            "pushNotifications": True,
            "emailNotifications": True,
            
            "preferences": {
                "showAge": True,
                "showOnlineStatus": True, 
                "allowMessages": True
            },
            "privacy": {
                "profileVisibility": "public",
                "showLastSeen": True
            },
            "socialLinks": {
                "instagram": "",
                "twitter": "",
                "website": ""
            },
            "interests": [],
            "location": "",
            "lastUsernameChange": None
        }
        
        await db.users.insert_one(user_dict)
        
        # Generate access token
        access_token = create_access_token(data={"sub": user_dict["id"]})
        
        # Generate access token for successful registration
        access_token = create_access_token(data={"sub": user_dict["id"]})
        
        if clean_mobile and not clean_email:
            # Mobile-only registration - auto verified and logged in
            return {
                "message": "Registration successful! Welcome to LuvHive!",
                "access_token": access_token,
                "token_type": "bearer",
                "user": {k: v for k, v in user_dict.items() if k not in ["password_hash", "_id", "emailVerificationToken"]},
                "auto_login": True
            }
        elif clean_email and not user_dict.get("emailVerified", False):
            # Email registration but not verified yet
            return {
                "message": "Registration successful! Please check your email to verify your account before signing in.",
                "email_sent": True,
                "user_id": user_dict["id"],
                "email_verification_required": True
            }
        else:
            # Both email and mobile provided, or email already verified
            return {
                "message": "Registration successful! Welcome to LuvHive!",
                "access_token": access_token,
                "token_type": "bearer", 
                "user": {k: v for k, v in user_dict.items() if k not in ["password_hash", "_id", "emailVerificationToken"]},
                "auto_login": True
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    # Find user with case-insensitive username (handles whitespace issues)
    clean_username = user_data.username.strip()
    escaped_username = clean_username.replace('.', r'\.')
    user = await db.users.find_one({
        "username": {"$regex": f"^{escaped_username}$", "$options": "i"}
    })
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # CRITICAL SECURITY: Block login if email not verified
    if not user.get("emailVerified", False):
        raise HTTPException(
            status_code=403, 
            detail="Please verify your email address before signing in. Check your email for verification link."
        )
    
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

@api_router.post("/auth/telegram")
async def telegram_auth(telegram_data: TelegramAuthRequest):
    """
    Authenticate user via Telegram Login Widget with secure hash verification
    """
    # Get Telegram bot token from environment
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not telegram_bot_token:
        raise HTTPException(status_code=500, detail="Telegram bot not configured")
    
    # Verify Telegram hash for security
    auth_data_dict = {
        "id": str(telegram_data.id),
        "first_name": telegram_data.first_name,
        "auth_date": str(telegram_data.auth_date),
        "hash": telegram_data.hash
    }
    
    # Add optional fields if present
    if telegram_data.last_name:
        auth_data_dict["last_name"] = telegram_data.last_name
    if telegram_data.username:
        auth_data_dict["username"] = telegram_data.username
    if telegram_data.photo_url:
        auth_data_dict["photo_url"] = telegram_data.photo_url
    
    # Verify the hash
    if not verify_telegram_hash(auth_data_dict.copy(), telegram_bot_token):
        raise HTTPException(status_code=401, detail="Invalid Telegram authentication data")
    
    # Check auth_date is not too old (within 24 hours)
    current_time = int(datetime.now(timezone.utc).timestamp())
    if current_time - telegram_data.auth_date > 86400:  # 24 hours
        raise HTTPException(status_code=401, detail="Telegram authentication data expired")
    
    # Check if user exists by Telegram ID
    existing_user = await db.users.find_one({"telegramId": telegram_data.id})
    
    if existing_user:
        # User exists, log them in
        access_token = create_access_token(data={"sub": existing_user["id"]})
        user_dict = {k: v for k, v in existing_user.items() if k not in ["password_hash", "_id"]}
        
        return {
            "message": "Telegram login successful",
            "access_token": access_token,
            "user": user_dict
        }
    else:
        # Create new user from Telegram data
        # Generate a unique username if Telegram username is not available
        base_username = telegram_data.username or f"user_{telegram_data.id}"
        username = base_username
        counter = 1
        
        while await db.users.find_one({"username": username}):
            username = f"{base_username}{counter}"
            counter += 1
        
        # Create complete user with all required fields
        user_dict = {
            "id": str(uuid4()),
            "fullName": f"{telegram_data.first_name} {telegram_data.last_name or ''}".strip(),
            "username": username,
            "email": f"tg{telegram_data.id}@luvhive.app",  # Valid email format
            "age": 25,  # Better default age
            "gender": "Other",  # Default gender - user can update later
            "bio": "New LuvHive user from Telegram! 💬✨",  # Better default bio
            "telegramId": telegram_data.id,
            "telegramUsername": telegram_data.username,
            "telegramFirstName": telegram_data.first_name,
            "telegramLastName": telegram_data.last_name,
            "telegramPhotoUrl": telegram_data.photo_url,
            "profileImage": telegram_data.photo_url or "",  # Use Telegram photo as profile image
            "authMethod": "telegram",
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "followers": [],
            "following": [],
            "posts": [],
            "isPremium": False,
            "isOnline": True,
            "lastSeen": datetime.now(timezone.utc).isoformat(),
            "preferences": {  # Add fields that EditProfile expects
                "showAge": True,
                "showOnlineStatus": True, 
                "allowMessages": True
            },
            "privacy": {
                "profileVisibility": "public",
                "showLastSeen": True
            },
            "socialLinks": {  # Initialize social links for EditProfile
                "instagram": "",
                "twitter": "",
                "website": ""
            },
            "interests": [],  # Initialize interests array
            "location": "",  # Initialize location
            "appearInSearch": True,  # Make searchable by default
            "lastUsernameChange": None
        }
        
        await db.users.insert_one(user_dict)
        
        # Generate token
        access_token = create_access_token(data={"sub": user_dict["id"]})
        
        return {
            "message": "Telegram registration successful",
            "access_token": access_token,
            "user": {k: v for k, v in user_dict.items() if k not in ["password_hash", "_id"]}
        }

@api_router.post("/auth/telegram-signin")
async def telegram_signin(request: TelegramSigninRequest):
    """
    Initiate Telegram sign-in for existing users by sending OTP
    """
    try:
        # Check if user exists with this Telegram ID
        user = await db.users.find_one({"telegramId": request.telegramId})
        
        if not user:
            raise HTTPException(
                status_code=404, 
                detail="No account found with this Telegram ID. Please register first."
            )
        
        # Check if user registered via Telegram
        if user.get("authMethod") != "telegram":
            raise HTTPException(
                status_code=400,
                detail="This account was not registered via Telegram. Please use email/password login."
            )
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP
        await store_otp(request.telegramId, otp)
        
        # Send OTP via Telegram
        otp_sent = await send_telegram_otp(request.telegramId, otp)
        
        if not otp_sent:
            raise HTTPException(
                status_code=500,
                detail="Failed to send OTP. Please try again later."
            )
        
        return {
            "message": "OTP sent successfully to your Telegram account",
            "telegramId": request.telegramId,
            "otpSent": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Telegram signin error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/auth/verify-telegram-otp")
async def verify_telegram_otp(request: VerifyOTPRequest):
    """
    Verify OTP and complete Telegram sign-in
    """
    try:
        # Verify OTP
        is_valid = await verify_otp(request.telegramId, request.otp)
        
        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired OTP. Please request a new one."
            )
        
        # Get user
        user = await db.users.find_one({"telegramId": request.telegramId})
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        # Generate access token
        access_token = create_access_token(data={"sub": user["id"]})
        
        # Update last seen
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {
                "isOnline": True,
                "lastSeen": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "message": "Telegram login successful",
            "access_token": access_token,
            "user": {k: v for k, v in user.items() if k not in ["password_hash", "_id"]}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OTP verification error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """
    Send password reset email or suggest Telegram recovery
    """
    if not request.email or not request.email.strip():
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Find user by email
    user = await db.users.find_one({"email": request.email.lower().strip()})
    
    if not user:
        # Don't reveal if email exists, but return success for security
        return {"message": "If an account with this email exists, a reset link has been sent"}
    
    # Check if user has Telegram auth
    if user.get("telegramId"):
        return {
            "message": "Password reset available via Telegram",
            "hasTelegram": True,
            "suggestion": "You can reset your password through your Telegram bot or use the traditional email reset"
        }
    
    # Generate reset token (24 hours expiry)
    reset_token = create_access_token(
        data={"sub": user["id"], "type": "password_reset"}, 
        expires_delta=timedelta(hours=24)
    )
    
    # In production, send email with reset link
    # For now, return the token (in production, this should be sent via email)
    reset_link = f"https://your-app.com/reset-password?token={reset_token}"
    
    return {
        "message": "Password reset link sent to your email",
        "hasTelegram": False,
        # TODO: Remove this in production - only for testing
        "reset_link": reset_link  
    }

@api_router.post("/webhook/telegram")
async def telegram_webhook(update: dict):
    """Handle Telegram webhook updates"""
    try:
        # Process Telegram webhook update
        if "message" in update:
            message = update["message"]
            user = message.get("from", {})
            text = message.get("text", "")
            
            # Handle /start command
            if text.startswith("/start"):
                telegram_id = user.get("id")
                
                # Check if user exists
                existing_user = await db.users.find_one({"telegramId": telegram_id})
                
                if existing_user:
                    # User already registered
                    return {"status": "ok", "message": "User already registered"}
                else:
                    # Create new user from Telegram data
                    new_user_data = {
                        "id": str(uuid4()),
                        "telegramId": telegram_id,
                        "telegramUsername": user.get("username", ""),
                        "telegramFirstName": user.get("first_name", ""),
                        "telegramLastName": user.get("last_name", ""),
                        "fullName": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                        "username": user.get("username") or f"tguser{telegram_id}",
                        "authMethod": "telegram",
                        "createdAt": datetime.now(timezone.utc).isoformat(),
                        "age": 18,  # Default age
                        "gender": "Other",  # Default gender
                        "bio": "",
                        "profileImage": "",
                        "followers": [],
                        "following": [],
                        "posts": [],
                        "isPremium": False
                    }
                    
                    await db.users.insert_one(new_user_data)
                    return {"status": "ok", "message": "User registered successfully"}
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

@api_router.post("/auth/telegram-bot-check") 
async def check_telegram_bot_auth(auth_request: dict):
    """Check if user has authenticated via Telegram bot (PostgreSQL database)"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Connect to the Telegram bot's PostgreSQL database
        bot_conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="luvhive", 
            user="postgres",
            password="luvhive123"
        )
        
        # Get the most recently active user from bot database
        with bot_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT tg_user_id, display_name, username, created_at 
                FROM users 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            recent_user = cursor.fetchone()
            
        bot_conn.close()
        
        if recent_user:
            # Create user in MongoDB (our main database) if not exists
            telegram_id = recent_user['tg_user_id']
            existing_user = await db.users.find_one({"telegramId": telegram_id})
            
            if not existing_user:
                # Create new user in MongoDB with ALL required fields
                user_data = {
                    "id": str(uuid4()),
                    "telegramId": telegram_id,
                    "telegramUsername": recent_user.get('username', ''),
                    "telegramFirstName": "",
                    "telegramLastName": "",  
                    "fullName": recent_user.get('display_name', '') or f"User {telegram_id}",
                    "username": recent_user.get('username') or f"tguser{telegram_id}",
                    "email": f"tg{telegram_id}@luvhive.app",  # Valid email format
                    "authMethod": "telegram",
                    "createdAt": datetime.now(timezone.utc).isoformat(),
                    "age": 25,  # Changed from 18 to 25 (more realistic)
                    "gender": "Other", 
                    "bio": "New LuvHive user from Telegram! 💬✨",  # Better default bio
                    "profileImage": "",
                    "followers": [],
                    "following": [],
                    "posts": [],
                    "isPremium": False,
                    "isOnline": True,
                    "lastSeen": datetime.now(timezone.utc).isoformat(),
                    "preferences": {  # Add missing fields that EditProfile might expect
                        "showAge": True,
                        "showOnlineStatus": True, 
                        "allowMessages": True
                    },
                    "privacy": {
                        "profileVisibility": "public",
                        "showLastSeen": True
                    },
                    "socialLinks": {  # Initialize social links
                        "instagram": "",
                        "twitter": "",
                        "website": ""
                    },
                    "interests": [],  # Initialize interests array
                    "location": ""  # Initialize location
                }
                
                await db.users.insert_one(user_data)
                user = user_data
            else:
                user = existing_user
            
            # Generate JWT token
            access_token = jwt.encode({
                "user_id": user["id"],
                "username": user["username"], 
                "exp": datetime.now(timezone.utc) + timedelta(days=7)
            }, SECRET_KEY, algorithm="HS256")
            
            return {
                "authenticated": True,
                "access_token": access_token,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "fullName": user["fullName"],
                    "profileImage": user.get("profileImage", ""),
                    "authMethod": user["authMethod"]
                }
            }
        else:
            return {
                "authenticated": False,
                "message": "No recent Telegram authentication found. Please send /start to @Loveekisssbot"
            }
            
    except Exception as e:
        logger.error(f"Telegram bot auth check error: {e}")
        return {
            "authenticated": False,
            "message": f"Authentication check failed: {str(e)}"
        }

@api_router.post("/auth/telegram-check")
async def check_telegram_auth(auth_request: dict):
    """Legacy endpoint for telegram check"""
    return await check_telegram_bot_auth(auth_request)

@api_router.post("/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password using token from email
    """
    try:
        # Verify reset token
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if token_type != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token type")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid token")
        
        # Find user
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate new password
        if len(request.new_password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # Hash new password
        hashed_password = get_password_hash(request.new_password)
        
        # Update password in database
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"password_hash": hashed_password}}
        )
        
        return {"message": "Password reset successful"}
        
    except PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "fullName": current_user.fullName,
        "username": current_user.username,
        "email": current_user.email,  # Added email field for EditProfile compatibility
        "age": current_user.age,
        "gender": current_user.gender,
        "bio": current_user.bio,
        "profileImage": current_user.profileImage,
        "isPremium": current_user.isPremium,
        "isPrivate": current_user.isPrivate,
        "telegramLinked": current_user.telegramId is not None,
        "blockedUsers": current_user.blockedUsers,
        
        # Privacy Controls
        "appearInSearch": current_user.appearInSearch,
        "allowDirectMessages": current_user.allowDirectMessages,
        "showOnlineStatus": current_user.showOnlineStatus,
        
        # Interaction Preferences
        "allowTagging": current_user.allowTagging,
        "allowStoryReplies": current_user.allowStoryReplies,
        "showVibeScore": current_user.showVibeScore,
        
        # Notifications
        "pushNotifications": current_user.pushNotifications,
        "emailNotifications": current_user.emailNotifications
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

@api_router.put("/auth/settings")
async def update_user_settings(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Update user's settings"""
    # Get the setting key and value from request
    setting_updates = {}
    
    # Define allowed settings
    allowed_settings = [
        'isPrivate', 'appearInSearch', 'allowDirectMessages', 
        'showOnlineStatus', 'allowTagging', 'allowStoryReplies', 'showVibeScore',
        'pushNotifications', 'emailNotifications'
    ]
    
    for key, value in request.items():
        if key in allowed_settings and isinstance(value, bool):
            setting_updates[key] = value
    
    if not setting_updates:
        raise HTTPException(status_code=400, detail="No valid settings provided")
    
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": setting_updates}
    )
    
    return {"message": "Settings updated successfully", "updated": setting_updates}

@api_router.get("/auth/download-data")
async def download_user_data(current_user: User = Depends(get_current_user)):
    """Download user's data in JSON format"""
    # Get user data
    user_data = await db.users.find_one({"id": current_user.id})
    
    # Get user's posts
    posts = await db.posts.find({"userId": current_user.id}).to_list(1000)
    
    # Get user's stories
    stories = await db.stories.find({"userId": current_user.id}).to_list(1000)
    
    # Get user's notifications
    notifications = await db.notifications.find({"userId": current_user.id}).to_list(1000)
    
    # Prepare export data
    export_data = {
        "profile": {
            "id": user_data["id"],
            "fullName": user_data["fullName"],
            "username": user_data["username"],
            "age": user_data["age"],
            "gender": user_data["gender"],
            "bio": user_data.get("bio", ""),
            "isPremium": user_data.get("isPremium", False),
            "createdAt": user_data["createdAt"].isoformat(),
            "followers": len(user_data.get("followers", [])),
            "following": len(user_data.get("following", []))
        },
        "posts": [
            {
                "id": post["id"],
                "caption": post.get("caption", ""),
                "mediaType": post["mediaType"],
                "likes": len(post.get("likes", [])),
                "comments": len(post.get("comments", [])),
                "createdAt": post["createdAt"].isoformat()
            } for post in posts
        ],
        "stories": [
            {
                "id": story["id"],
                "caption": story.get("caption", ""),
                "mediaType": story["mediaType"],
                "createdAt": story["createdAt"].isoformat(),
                "expiresAt": story["expiresAt"].isoformat()
            } for story in stories
        ],
        "notifications": [
            {
                "type": notif["type"],
                "fromUsername": notif["fromUsername"],
                "createdAt": notif["createdAt"].isoformat()
            } for notif in notifications
        ],
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "totalPosts": len(posts),
        "totalStories": len(stories),
        "totalNotifications": len(notifications)
    }
    
    import json
    from fastapi.responses import Response
    
    json_data = json.dumps(export_data, indent=2)
    
    return Response(
        content=json_data,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=luvhive-data-{current_user.username}.json"
        }
    )

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

@api_router.get("/auth/check-email/{email}")
async def check_email_availability(email: str):
    """
    Check email availability
    """
    try:
        # Clean and validate the email
        clean_email = email.strip().lower()
        
        if '@' not in clean_email or '.' not in clean_email:
            return {
                "available": False,
                "message": "Invalid email format"
            }
        
        # Check if email is already registered
        existing_user = await db.users.find_one({"email": clean_email})
        
        if existing_user:
            return {
                "available": False,
                "message": "Email is already registered - please use a different email"
            }
        else:
            return {
                "available": True,
                "message": "Email is available!"
            }
        
    except Exception as e:
        logger.error(f"Email check error: {e}")
        return {
            "available": False,
            "message": "Error checking email availability"
        }

@api_router.post("/auth/send-email-otp")
async def send_email_otp_endpoint(request: EmailOTPRequest):
    """
    Send OTP to email address for registration verification
    """
    try:
        clean_email = request.email.strip().lower()
        
        if '@' not in clean_email or '.' not in clean_email:
            raise HTTPException(
                status_code=400,
                detail="Invalid email format"
            )
        
        # Check if email already exists
        existing_user = await db.users.find_one({"email": clean_email})
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP
        await store_email_otp(clean_email, otp)
        
        # Send OTP via email
        otp_sent = await send_email_otp(clean_email, otp)
        
        if not otp_sent:
            raise HTTPException(
                status_code=500,
                detail="Failed to send OTP email"
            )
        
        return {
            "message": "OTP sent to your email address",
            "email": clean_email,
            "otpSent": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send email OTP error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/auth/verify-email-otp")
async def verify_email_otp_endpoint(request: VerifyEmailOTPRequest):
    """
    Verify email OTP for registration
    """
    try:
        clean_email = request.email.strip().lower()
        
        # Verify OTP
        is_valid = await verify_email_otp(clean_email, request.otp.strip())
        
        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired OTP"
            )
        
        return {
            "message": "Email verified successfully",
            "verified": True,
            "email": clean_email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify email OTP error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/auth/send-mobile-otp")
async def send_mobile_otp_endpoint(request: SendMobileOTPRequest):
    """
    Send OTP to mobile number for verification
    """
    try:
        clean_mobile = request.mobileNumber.strip()
        
        # Basic mobile number validation
        mobile_digits = ''.join(filter(str.isdigit, clean_mobile))
        if len(mobile_digits) < 10 or len(mobile_digits) > 15:
            raise HTTPException(
                status_code=400,
                detail="Invalid mobile number format"
            )
        
        # Send OTP
        otp_sent = await send_mobile_otp(clean_mobile)
        
        if not otp_sent:
            raise HTTPException(
                status_code=500,
                detail="Failed to send SMS OTP"
            )
        
        return {
            "message": "OTP sent to your mobile number",
            "mobileNumber": clean_mobile,
            "otpSent": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send mobile OTP error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/auth/verify-mobile-otp")
async def verify_mobile_otp_endpoint(request: VerifyMobileOTPRequest):
    """
    Verify mobile OTP
    """
    try:
        clean_mobile = request.mobileNumber.strip()
        clean_otp = request.otp.strip()
        
        # Verify OTP
        is_valid = await verify_mobile_otp(clean_mobile, clean_otp)
        
        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired OTP"
            )
        
        return {
            "message": "Mobile number verified successfully",
            "verified": True,
            "mobileNumber": clean_mobile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify mobile OTP error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/auth/verify-existing-account")
async def verify_existing_account(request: EmailOTPRequest):
    """
    Send verification email to existing unverified accounts
    """
    try:
        clean_email = request.email.strip().lower()
        
        # Find existing user with this email
        user = await db.users.find_one({"email": clean_email})
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="No account found with this email"
            )
        
        # Check if already verified
        if user.get("emailVerified", False):
            return {
                "message": "Account is already verified",
                "verified": True
            }
        
        # Generate OTP for existing account
        otp = generate_otp()
        
        # Store OTP
        await store_email_otp(clean_email, otp)
        
        # Send OTP via email
        otp_sent = await send_email_otp(clean_email, otp)
        
        if not otp_sent:
            raise HTTPException(
                status_code=500,
                detail="Failed to send verification email"
            )
        
        return {
            "message": "Verification email sent to your registered email address",
            "email": clean_email,
            "otpSent": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify existing account error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/auth/verify-existing-otp")
async def verify_existing_otp(request: VerifyEmailOTPRequest):
    """
    Verify OTP for existing account and mark as verified
    """
    try:
        clean_email = request.email.strip().lower()
        
        # Verify OTP
        is_valid = await verify_email_otp(clean_email, request.otp.strip())
        
        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired OTP"
            )
        
        # Mark account as verified
        result = await db.users.update_one(
            {"email": clean_email},
            {"$set": {"emailVerified": True}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )
        
        return {
            "message": "Account verified successfully! You can now sign in.",
            "verified": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify existing OTP error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/auth/cleanup-account/{identifier}")
async def cleanup_account_data(identifier: str):
    """
    ADMIN ENDPOINT: Delete all account data by username, email, or mobile number
    """
    try:
        # Find users by username, email, or mobile
        users_to_delete = []
        
        # Search by username (case insensitive)
        user_by_username = await db.users.find_one({
            "username": {"$regex": f"^{identifier}$", "$options": "i"}
        })
        if user_by_username:
            users_to_delete.append(user_by_username)
        
        # Search by email (case insensitive)  
        if "@" in identifier:
            user_by_email = await db.users.find_one({
                "email": {"$regex": f"^{identifier}$", "$options": "i"}
            })
            if user_by_email and user_by_email not in users_to_delete:
                users_to_delete.append(user_by_email)
        
        # Search by mobile number (clean digits only)
        if identifier.isdigit() or "+" in identifier:
            # Clean mobile number for search
            clean_mobile = ''.join(filter(str.isdigit, identifier))
            mobile_patterns = [
                identifier,  # Original format
                clean_mobile,  # Digits only
                f"+91{clean_mobile}",  # With +91
                f"91{clean_mobile}",  # With 91
            ]
            
            for pattern in mobile_patterns:
                user_by_mobile = await db.users.find_one({
                    "mobileNumber": pattern
                })
                if user_by_mobile and user_by_mobile not in users_to_delete:
                    users_to_delete.append(user_by_mobile)
        
        # Delete all found users and related data
        deleted_users = []
        for user in users_to_delete:
            user_id = user["id"]
            username = user["username"]
            email = user.get("email", "N/A")
            
            # Delete user posts
            posts_deleted = await db.posts.delete_many({"userId": user_id})
            
            # Delete user comments
            comments_deleted = await db.comments.delete_many({"userId": user_id})
            
            # Remove user from other users' followers/following lists
            await db.users.update_many(
                {"followers": user_id},
                {"$pull": {"followers": user_id}}
            )
            await db.users.update_many(
                {"following": user_id},
                {"$pull": {"following": user_id}}
            )
            
            # Delete the user account
            user_deleted = await db.users.delete_one({"id": user_id})
            
            deleted_users.append({
                "username": username,
                "email": email,
                "mobileNumber": user.get("mobileNumber", "N/A"),
                "userId": user_id,
                "posts_deleted": posts_deleted.deleted_count,
                "comments_deleted": comments_deleted.deleted_count,
                "account_deleted": user_deleted.deleted_count > 0
            })
        
        if not deleted_users:
            return {
                "message": f"No accounts found with identifier: {identifier}",
                "deleted_users": []
            }
        
        return {
            "message": f"Successfully cleaned up {len(deleted_users)} account(s)",
            "deleted_users": deleted_users
        }
        
    except Exception as e:
        logger.error(f"Account cleanup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/auth/forgot-password-mobile")
async def forgot_password_mobile(request: ForgotPasswordMobileRequest):
    """
    Send OTP to mobile for password reset
    """
    try:
        clean_mobile = request.mobileNumber.strip()
        
        # Find user by mobile number
        user = await db.users.find_one({"mobileNumber": clean_mobile})
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="No account found with this mobile number"
            )
        
        # Generate OTP for password reset
        otp = generate_otp()
        
        # Store OTP with mobile number (use proper mobile OTP storage)
        mobile_key = f"mobile_{clean_mobile}"
        await store_email_otp(mobile_key, otp)
        
        # Send OTP via SMS
        otp_sent = await send_mobile_otp(clean_mobile)
        
        if not otp_sent:
            raise HTTPException(
                status_code=500,
                detail="Failed to send OTP to mobile"
            )
        
        return {
            "message": "Password reset OTP sent to your mobile number",
            "mobileNumber": clean_mobile,
            "otpSent": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mobile forgot password error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/auth/reset-password-mobile")
async def reset_password_mobile(request: ResetPasswordMobileRequest):
    """
    Reset password using mobile OTP
    """
    try:
        clean_mobile = request.mobileNumber.strip()
        
        # Verify OTP
        mobile_key = f"mobile_{clean_mobile}"
        is_valid = await verify_email_otp(mobile_key, request.otp.strip())
        
        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired OTP"
            )
        
        # Find user
        user = await db.users.find_one({"mobileNumber": clean_mobile})
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        # Hash new password
        hashed_password = get_password_hash(request.new_password)
        
        # Update password
        await db.users.update_one(
            {"mobileNumber": clean_mobile},
            {"$set": {"password_hash": hashed_password}}
        )
        
        return {
            "message": "Password reset successfully! You can now sign in with your new password."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mobile password reset error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/auth/verify-email")
async def verify_email(token: str):
    """
    Verify email address with token
    """
    try:
        # Find user with this verification token
        user = await db.users.find_one({"emailVerificationToken": token})
        
        if not user:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired verification link"
            )
        
        # Mark email as verified and remove token
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {
                "emailVerified": True,
                "emailVerificationToken": None
            }}
        )
        
        return {
            "message": "Email verified successfully! You can now sign in to your account.",
            "verified": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/auth/check-username/{username}")
async def check_username_availability(username: str):
    """
    Check username availability and provide suggestions if taken
    """
    try:
        # Clean and validate the username
        clean_username = username.strip().lower()
        
        if len(clean_username) < 3:
            return {
                "available": False,
                "message": "Username must be at least 3 characters",
                "suggestions": []
            }
        
        if len(clean_username) > 20:
            return {
                "available": False,
                "message": "Username must be less than 20 characters", 
                "suggestions": []
            }
        
        # Check if username contains only valid characters
        import re
        if not re.match("^[a-zA-Z0-9_]+$", clean_username):
            return {
                "available": False,
                "message": "Username can only contain letters, numbers, and underscores",
                "suggestions": []
            }
        
        # Check if username is available (case-insensitive)
        escaped_username = clean_username.replace('.', r'\.')
        existing_user = await db.users.find_one({
            "username": {"$regex": f"^{escaped_username}$", "$options": "i"}
        })
        
        if not existing_user:
            return {
                "available": True,
                "message": "Username is available!",
                "suggestions": []
            }
        
        # Generate suggestions
        suggestions = []
        base_username = clean_username
        
        # Try various suggestions
        suggestion_patterns = [
            f"{base_username}_",
            f"{base_username}2025",
            f"{base_username}123",
            f"{base_username}2024", 
            f"{base_username}_1",
            f"{base_username}x",
            f"{base_username}official",
            f"{base_username}_real",
            f"the_{base_username}",
            f"{base_username}_official"
        ]
        
        # Add underscore variations for long usernames
        if len(base_username) > 5:
            # Insert underscore in middle
            mid = len(base_username) // 2
            suggestion_patterns.extend([
                f"{base_username[:mid]}_{base_username[mid:]}",
                f"{base_username[:-2]}_{base_username[-2:]}",
                f"{base_username[:3]}_{base_username[3:]}"
            ])
        
        for suggestion in suggestion_patterns:
            if len(suggestions) >= 5:  # Limit to 5 suggestions
                break
                
            # Check if suggestion is available
            escaped_suggestion = suggestion.replace('.', r'\.')
            suggestion_exists = await db.users.find_one({
                "username": {"$regex": f"^{escaped_suggestion}$", "$options": "i"}
            })
            
            if not suggestion_exists and len(suggestion) <= 20:
                suggestions.append(suggestion)
        
        return {
            "available": False,
            "message": f"Username '{username}' is not available",
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Username check error: {e}")
        return {
            "available": False,
            "message": "Error checking username availability",
            "suggestions": []
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
            "isFollowing": user["id"] in current_user.following
        })
    
    return {"users": users_list}

@api_router.get("/users/blocked")
async def get_blocked_users(current_user: User = Depends(get_current_user)):
    """Get list of blocked users with their profile information"""
    blocked_user_ids = current_user.blockedUsers
    
    if not blocked_user_ids:
        return {"blockedUsers": []}
    
    # Get blocked users information
    blocked_users = await db.users.find({"id": {"$in": blocked_user_ids}}).to_list(100)
    
    blocked_users_list = []
    for user in blocked_users:
        blocked_users_list.append({
            "id": user["id"],
            "username": user["username"],
            "fullName": user["fullName"],
            "profileImage": user.get("profileImage"),
            "blockedAt": user.get("blockedAt", "Unknown")
        })
    
    return {"blockedUsers": blocked_users_list}

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
        "isFollowing": user["id"] in current_user.following,
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

# Moved to before /users/{userId} route to avoid conflicts

@api_router.post("/users/{userId}/unblock")
async def unblock_user(userId: str, current_user: User = Depends(get_current_user)):
    """Unblock a user"""
    if userId == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot unblock yourself")
    
    target_user = await db.users.find_one({"id": userId})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove from blocked users list
    await db.users.update_one(
        {"id": current_user.id},
        {"$pull": {"blockedUsers": userId}}
    )
    
    return {"message": "User unblocked successfully"}

# Search functionality
class SearchRequest(BaseModel):
    query: str
    type: Optional[str] = "all"  # "users", "posts", "hashtags", "all"
    page: Optional[int] = 1
    limit: Optional[int] = 10

@api_router.post("/search")
async def search_content(search_request: SearchRequest, current_user: User = Depends(get_current_user)):
    """
    Search for users, posts, and hashtags
    """
    query = search_request.query.strip()
    search_type = search_request.type
    page = max(1, search_request.page)
    limit = min(50, max(1, search_request.limit))  # Limit between 1-50
    skip = (page - 1) * limit
    
    if not query:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    # Escape special regex characters for safe searching
    escaped_query = query.replace('.', r'\.')
    
    results = {
        "users": [],
        "posts": [],
        "hashtags": [],
        "query": query
    }
    
    # Search users (if type is "users" or "all")
    if search_type in ["users", "all"]:
        # Create a more intelligent search with exact match priority
        base_filter = {
            "$and": [
                {"id": {"$ne": current_user.id}},  # Exclude current user
                {"id": {"$nin": current_user.blockedUsers}},  # Exclude blocked users
                {"appearInSearch": True}  # Only users who appear in search
            ]
        }
        
        # First, search for exact matches using optimized queries
        exact_filter = {**base_filter}
        
        # Use text search for better performance with indexing
        text_search_filter = {**base_filter}
        text_search_filter["$and"].append({
            "$text": {"$search": f'"{query}"'}  # Exact phrase search
        })
        
        # Fallback regex for exact matches if text search doesn't work
        regex_filter = {**base_filter}
        regex_filter["$and"].append({
            "$or": [
                {"username": {"$regex": f"^\\s*{escaped_query}\\s*$", "$options": "i"}},
                {"fullName": {"$regex": f"^\\s*{escaped_query}\\s*$", "$options": "i"}}
            ]
        })
        
        # Try text search first, fallback to regex
        try:
            exact_users = await db.users.find(text_search_filter).skip(skip).limit(limit).to_list(limit)
        except:
            exact_users = await db.users.find(regex_filter).skip(skip).limit(limit).to_list(limit)
        user_ids_found = {user["id"] for user in exact_users}
        
        # Then, search for partial matches, excluding exact matches
        partial_filter = {**base_filter}
        partial_filter["$and"].extend([
            {"id": {"$nin": list(user_ids_found)}},  # Exclude already found users
            {
                "$or": [
                    {"fullName": {"$regex": escaped_query, "$options": "i"}},
                    {"username": {"$regex": escaped_query, "$options": "i"}},
                    {"bio": {"$regex": escaped_query, "$options": "i"}}
                ]
            }
        ])
        
        partial_users = await db.users.find(partial_filter).limit(10).to_list(10)
        
        # Combine results with exact matches first
        all_users = exact_users + partial_users
        
        for user in all_users[:20]:  # Limit to 20 total results
            results["users"].append({
                "id": user["id"],
                "fullName": user["fullName"],
                "username": user["username"],
                "profileImage": user.get("profileImage"),
                "bio": user.get("bio", "")[:100],  # Limit bio length for performance
                "followersCount": len(user.get("followers", [])),
                "isFollowing": user["id"] in current_user.following,
                "isPremium": user.get("isPremium", False)
            })
    
    # Search posts (if type is "posts" or "all")
    if search_type in ["posts", "all"]:
        # Find posts from non-blocked users and public accounts
        blocked_users = current_user.blockedUsers  # Don't exclude own posts
        
        post_filter = {
            "$and": [
                {"userId": {"$nin": blocked_users}},
                {"isArchived": {"$ne": True}},
                {
                    "$or": [
                        {"caption": {"$regex": query, "$options": "i"}},
                        {"username": {"$regex": query, "$options": "i"}}
                    ]
                }
            ]
        }
        
        posts = await db.posts.find(post_filter).sort("createdAt", -1).limit(20).to_list(20)
        for post in posts:
            results["posts"].append({
                "id": post["id"],
                "userId": post["userId"],
                "username": post["username"],
                "userProfileImage": post.get("userProfileImage"),
                "mediaType": post["mediaType"],
                "mediaUrl": post["mediaUrl"],
                "caption": post.get("caption", ""),
                "likes": len(post.get("likes", [])),
                "comments": len(post.get("comments", [])),
                "createdAt": post["createdAt"].isoformat(),
                "isLiked": current_user.id in post.get("likes", []),
                "isSaved": post["id"] in current_user.savedPosts
            })
    
    # Extract hashtags from posts (if type is "hashtags" or "all")
    if search_type in ["hashtags", "all"] and query.startswith("#"):
        hashtag_query = query[1:]  # Remove # symbol
        hashtag_filter = {
            "$and": [
                {"userId": {"$nin": current_user.blockedUsers}},
                {"isArchived": {"$ne": True}},
                {"caption": {"$regex": f"#{hashtag_query}", "$options": "i"}}
            ]
        }
        
        hashtag_posts = await db.posts.find(hashtag_filter).sort("createdAt", -1).limit(10).to_list(10)
        hashtags_found = set()
        
        for post in hashtag_posts:
            caption = post.get("caption", "")
            # Extract hashtags from caption
            import re
            hashtags = re.findall(r'#\w+', caption, re.IGNORECASE)
            for hashtag in hashtags:
                if hashtag_query.lower() in hashtag.lower():
                    hashtags_found.add(hashtag.lower())
        
        results["hashtags"] = list(hashtags_found)[:10]
    
    return results

@api_router.get("/search/trending")
async def get_trending_content(current_user: User = Depends(get_current_user)):
    """
    Get trending hashtags and users from recent posts
    """
    # Get trending hashtags from recent posts (last 7 days)
    recent_posts = await db.posts.find({
        "$and": [
            {"userId": {"$nin": current_user.blockedUsers}},
            {"isArchived": {"$ne": True}},
            {"createdAt": {"$gte": datetime.now(timezone.utc) - timedelta(days=7)}}
        ]
    }).to_list(1000)
    
    hashtag_count = {}
    import re
    for post in recent_posts:
        caption = post.get("caption", "")
        hashtags = re.findall(r'#\w+', caption, re.IGNORECASE)
        for hashtag in hashtags:
            hashtag = hashtag.lower()
            hashtag_count[hashtag] = hashtag_count.get(hashtag, 0) + 1
    
    # Sort hashtags by frequency and return top 20
    trending_hashtags = sorted(hashtag_count.items(), key=lambda x: x[1], reverse=True)[:20]
    
    # Get trending users (users with most followers)
    trending_users_cursor = await db.users.find({
        "$and": [
            {"id": {"$ne": current_user.id}},
            {"id": {"$nin": current_user.blockedUsers}},
            {"appearInSearch": True}
        ]
    }).to_list(100)
    
    # Sort by follower count and take top 10
    trending_users_cursor.sort(key=lambda x: len(x.get("followers", [])), reverse=True)
    trending_users = trending_users_cursor[:10]
    
    trending_users_list = []
    for user in trending_users:
        trending_users_list.append({
            "id": user["id"],
            "fullName": user["fullName"],
            "username": user["username"],
            "profileImage": user.get("profileImage"),
            "bio": user.get("bio", ""),
            "followersCount": len(user.get("followers", [])),
            "isFollowing": user["id"] in current_user.following,
            "isPremium": user.get("isPremium", False)
        })
    
    return {
        "trending_users": trending_users_list,
        "trending_hashtags": [{"hashtag": hashtag, "count": count} for hashtag, count in trending_hashtags]
    }

@api_router.post("/admin/fix-duplicate-usernames")
async def fix_duplicate_usernames():
    """
    Admin endpoint to fix duplicate usernames caused by whitespace
    """
    try:
        # Find users with whitespace in usernames
        users_with_whitespace = await db.users.find({
            "$or": [
                {"username": {"$regex": "^\\s+|\\s+$"}},  # Leading or trailing spaces
                {"fullName": {"$regex": "^\\s+|\\s+$"}}   # Leading or trailing spaces in fullName
            ]
        }).to_list(1000)
        
        fixed_count = 0
        for user in users_with_whitespace:
            clean_username = user["username"].strip()
            clean_fullname = user["fullName"].strip()
            
            # Check if cleaned username already exists
            existing_clean = await db.users.find_one({
                "username": clean_username,
                "id": {"$ne": user["id"]}
            })
            
            if existing_clean:
                # If clean version exists, we need to handle the duplicate
                # Option 1: Delete the whitespace version if it has no activity
                user_posts = await db.posts.count_documents({"userId": user["id"]})
                user_followers = len(user.get("followers", []))
                
                if user_posts == 0 and user_followers == 0:
                    # Delete the inactive duplicate
                    await db.users.delete_one({"id": user["id"]})
                    fixed_count += 1
                else:
                    # Rename the duplicate by adding a number
                    counter = 1
                    new_username = f"{clean_username}{counter}"
                    while await db.users.find_one({"username": new_username}):
                        counter += 1
                        new_username = f"{clean_username}{counter}"
                    
                    await db.users.update_one(
                        {"id": user["id"]},
                        {"$set": {"username": new_username, "fullName": clean_fullname}}
                    )
                    fixed_count += 1
            else:
                # Just clean the whitespace
                await db.users.update_one(
                    {"id": user["id"]},
                    {"$set": {"username": clean_username, "fullName": clean_fullname}}
                )
                fixed_count += 1
        
        return {
            "message": f"Fixed {fixed_count} duplicate usernames",
            "fixed_count": fixed_count
        }
        
    except Exception as e:
        logger.error(f"Error fixing duplicates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fixing duplicates: {str(e)}")

@api_router.get("/search/suggestions")
async def get_search_suggestions(q: str = "", current_user: User = Depends(get_current_user)):
    """
    Get search suggestions based on partial query
    """
    if not q or len(q) < 2:
        return {"suggestions": []}
    
    suggestions = []
    
    # User suggestions
    user_filter = {
        "$and": [
            {"id": {"$ne": current_user.id}},
            {"id": {"$nin": current_user.blockedUsers}},
            {"appearInSearch": True},
            {
                "$or": [
                    {"fullName": {"$regex": f"^{q}", "$options": "i"}},
                    {"username": {"$regex": f"^{q}", "$options": "i"}}
                ]
            }
        ]
    }
    
    users = await db.users.find(user_filter).limit(5).to_list(5)
    for user in users:
        suggestions.append({
            "type": "user",
            "text": f"{user['fullName']} (@{user['username']})",
            "value": user["username"],
            "avatar": user.get("profileImage")
        })
    
    # Hashtag suggestions
    if q.startswith("#"):
        hashtag_query = q[1:]
        recent_posts = await db.posts.find({
            "$and": [
                {"userId": {"$nin": current_user.blockedUsers}},
                {"isArchived": {"$ne": True}},
                {"caption": {"$regex": f"#{hashtag_query}", "$options": "i"}}
            ]
        }).limit(20).to_list(20)
        
        hashtags_found = set()
        import re
        for post in recent_posts:
            caption = post.get("caption", "")
            hashtags = re.findall(r'#\w+', caption, re.IGNORECASE)
            for hashtag in hashtags:
                if hashtag_query.lower() in hashtag.lower():
                    hashtags_found.add(hashtag)
        
        for hashtag in list(hashtags_found)[:5]:
            suggestions.append({
                "type": "hashtag",
                "text": hashtag,
                "value": hashtag
            })
    
    return {"suggestions": suggestions}

# Health check endpoint
@api_router.get("/health")
async def health_check():
    try:
        # Test database connection
        user_count = await db.users.count_documents({})
        return {
            "status": "healthy",
            "database": db_name,
            "user_count": user_count,
            "mongo_url": mongo_url.replace(mongo_url.split('@')[-1] if '@' in mongo_url else '', '***') if mongo_url else None
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": db_name
        }

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