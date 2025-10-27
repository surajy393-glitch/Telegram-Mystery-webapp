"""
Social Platform Features for LuvHive
- Posts (Feed)
- Stories (24-hour content)
- Follow/Unfollow
- Likes, Comments, Shares
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from uuid import uuid4

# Setup logger
logger = logging.getLogger(__name__)

# Create router
social_router = APIRouter(prefix="/api/social", tags=["social"])

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "luvhive_database")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Pydantic Models
class CreatePostRequest(BaseModel):
    content: str
    postType: str = "text"  # text, image, video, poll
    isAnonymous: bool = False
    pollOptions: Optional[List[str]] = None
    
class CreateStoryRequest(BaseModel):
    content: str
    storyType: str = "text"  # text, image, video
    isAnonymous: bool = False

class CommentRequest(BaseModel):
    postId: str
    content: str
    isAnonymous: bool = False

class LikeRequest(BaseModel):
    postId: str
    reactionType: str = "like"  # like, love, fire, wow

# Helper Functions
async def get_current_user(token: str):
    """Get current user from token - placeholder"""
    # TODO: Implement proper JWT validation
    user = await db.users.find_one({"id": token})
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

# POSTS ENDPOINTS

@social_router.post("/posts")
async def create_post(
    content: str = Form(...),
    postType: str = Form("text"),
    isAnonymous: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    userId: str = Form(...)
):
    """Create a new post"""
    try:
        # Get user
        user = await db.users.find_one({"id": userId})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Handle image upload if provided
        image_url = None
        if image:
            # Save image
            upload_dir = "/app/uploads/posts"
            os.makedirs(upload_dir, exist_ok=True)
            
            file_ext = image.filename.split('.')[-1]
            filename = f"{uuid4()}.{file_ext}"
            file_path = os.path.join(upload_dir, filename)
            
            with open(file_path, "wb") as f:
                content_bytes = await image.read()
                f.write(content_bytes)
            
            image_url = f"/api/uploads/posts/{filename}"
        
        # Create post document
        post = {
            "id": str(uuid4()),
            "userId": userId if not isAnonymous else "anonymous",
            "username": user.get("username") if not isAnonymous else "Anonymous",
            "userAvatar": user.get("profileImage") if not isAnonymous else None,
            "content": content if content else "",  # Allow empty content if image is present
            "postType": postType,
            "imageUrl": image_url,
            "isAnonymous": isAnonymous,
            "likes": [],
            "comments": [],
            "shares": 0,
            "views": 0,
            "createdAt": datetime.now(timezone.utc),
            "city": user.get("city", "Unknown"),
            "age": user.get("age", 0),
            "gender": user.get("gender", "Unknown")
        }
        
        await db.posts.insert_one(post)
        
        return {
            "success": True,
            "message": "Post created successfully",
            "post": {
                "id": post["id"],
                "createdAt": post["createdAt"].isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_router.get("/feed")
async def get_feed(
    userId: str,
    skip: int = 0,
    limit: int = 20,
    city: Optional[str] = None
):
    """Get feed with posts"""
    try:
        # Build query
        query = {}
        
        # Filter by city if provided
        if city:
            query["city"] = city
        
        # Get posts sorted by recent
        posts = await db.posts.find(query)\
            .sort("createdAt", -1)\
            .skip(skip)\
            .limit(limit)\
            .to_list(limit)
        
        # Format posts
        formatted_posts = []
        for post in posts:
            # Get like count
            like_count = len(post.get("likes", []))
            comment_count = len(post.get("comments", []))
            
            # Check if current user liked
            user_liked = userId in post.get("likes", [])
            
            formatted_posts.append({
                "id": post["id"],
                "userId": post.get("userId"),
                "username": post.get("username"),
                "userAvatar": post.get("userAvatar"),
                "content": post.get("content"),
                "postType": post.get("postType"),
                "imageUrl": post.get("imageUrl"),
                "isAnonymous": post.get("isAnonymous", False),
                "likes": like_count,
                "comments": comment_count,
                "shares": post.get("shares", 0),
                "views": post.get("views", 0),
                "userLiked": user_liked,
                "createdAt": post["createdAt"].isoformat(),
                "timeAgo": get_time_ago(post["createdAt"])
            })
        
        return {
            "success": True,
            "posts": formatted_posts,
            "hasMore": len(formatted_posts) == limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_router.post("/posts/{postId}/like")
async def like_post(postId: str, userId: str = Form(...), reactionType: str = Form("like")):
    """Like/Unlike a post"""
    try:
        post = await db.posts.find_one({"id": postId})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        likes = post.get("likes", [])
        
        if userId in likes:
            # Unlike
            likes.remove(userId)
            action = "unliked"
        else:
            # Like
            likes.append(userId)
            action = "liked"
        
        # Update post
        await db.posts.update_one(
            {"id": postId},
            {"$set": {"likes": likes}}
        )
        
        return {
            "success": True,
            "action": action,
            "likeCount": len(likes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_router.post("/posts/{postId}/comment")
async def add_comment(
    postId: str,
    userId: str = Form(...),
    content: str = Form(...),
    isAnonymous: bool = Form(False)
):
    """Add comment to a post"""
    try:
        post = await db.posts.find_one({"id": postId})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        user = await db.users.find_one({"id": userId})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        comment = {
            "id": str(uuid4()),
            "userId": userId if not isAnonymous else "anonymous",
            "username": user.get("username") if not isAnonymous else "Anonymous",
            "userAvatar": user.get("profileImage") if not isAnonymous else None,
            "content": content,
            "createdAt": datetime.now(timezone.utc),
            "isAnonymous": isAnonymous
        }
        
        # Add comment to post
        await db.posts.update_one(
            {"id": postId},
            {"$push": {"comments": comment}}
        )
        
        # Create notification for post owner (if not commenting on own post and not anonymous)
        if not isAnonymous and post.get("userId") != userId:
            notification = {
                "id": str(uuid4()),
                "userId": post.get("userId"),
                "fromUserId": userId,
                "fromUsername": user.get("username", "Unknown"),
                "fromUserImage": user.get("profileImage"),
                "type": "comment",
                "postId": postId,
                "commentText": content[:50],  # Store first 50 chars
                "isRead": False,
                "createdAt": datetime.now(timezone.utc)
            }
            await db.notifications.insert_one(notification)
        
        return {
            "success": True,
            "comment": {
                "id": comment["id"],
                "content": comment["content"],
                "createdAt": comment["createdAt"].isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get comments for a post
@social_router.get("/posts/{postId}/comments")
async def get_post_comments(postId: str):
    """Get all comments for a post with nested replies"""
    try:
        post = await db.posts.find_one({"id": postId})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        comments = post.get("comments", [])
        
        # Organize comments and replies
        comment_map = {}
        root_comments = []
        
        for comment in comments:
            comment_id = comment.get("id")
            comment_data = {
                "id": comment_id,
                "userId": comment.get("userId"),
                "username": comment.get("username"),
                "userAvatar": comment.get("userAvatar"),
                "content": comment.get("content"),
                "createdAt": comment.get("createdAt"),
                "timeAgo": get_time_ago(comment.get("createdAt")),
                "likesCount": len(comment.get("likes", [])),
                "userLiked": False,  # TODO: Add user-specific like status
                "parentCommentId": comment.get("parentCommentId"),
                "replies": []
            }
            comment_map[comment_id] = comment_data
            
            if comment.get("parentCommentId"):
                # It's a reply
                parent_id = comment.get("parentCommentId")
                if parent_id in comment_map:
                    comment_map[parent_id]["replies"].append(comment_data)
            else:
                # It's a root comment
                root_comments.append(comment_data)
        
        return {"success": True, "comments": root_comments}
    except Exception as e:
        logger.error(f"Error fetching comments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Like a comment
@social_router.post("/comments/{commentId}/like")
async def like_comment(commentId: str, userId: str = Form(...)):
    """Like or unlike a comment"""
    try:
        # Find the post containing this comment
        post = await db.posts.find_one({"comments.id": commentId})
        if not post:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        comments = post.get("comments", [])
        comment_index = None
        
        for idx, comment in enumerate(comments):
            if comment.get("id") == commentId:
                comment_index = idx
                break
        
        if comment_index is None:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        comment = comments[comment_index]
        likes = comment.get("likes", [])
        
        if userId in likes:
            # Unlike
            likes.remove(userId)
        else:
            # Like
            likes.append(userId)
        
        comment["likes"] = likes
        comments[comment_index] = comment
        
        await db.posts.update_one(
            {"id": post["id"]},
            {"$set": {"comments": comments}}
        )
        
        return {"success": True, "likesCount": len(likes)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# get_time_ago function is defined in UTILITY FUNCTIONS section

# STORIES ENDPOINTS

@social_router.post("/stories")
async def create_story(
    userId: str = Form(...),
    content: str = Form(""),
    storyType: str = Form("image"),
    isAnonymous: bool = Form(False),
    image: Optional[UploadFile] = File(None)
):
    """Create a 24-hour story"""
    try:
        logger.info(f"Creating story for user: {userId}, type: {storyType}, has_image: {image is not None}")
        
        user = await db.users.find_one({"id": userId})
        if not user:
            logger.error(f"User not found: {userId}")
            raise HTTPException(status_code=404, detail="User not found")
        
        # Handle image upload
        image_url = None
        if image:
            upload_dir = "/app/uploads/stories"
            os.makedirs(upload_dir, exist_ok=True)
            
            file_ext = image.filename.split('.')[-1]
            filename = f"{uuid4()}.{file_ext}"
            file_path = os.path.join(upload_dir, filename)
            
            with open(file_path, "wb") as f:
                content_bytes = await image.read()
                f.write(content_bytes)
            
            image_url = f"/api/uploads/stories/{filename}"
        
        # Create story
        story = {
            "id": str(uuid4()),
            "userId": userId if not isAnonymous else "anonymous",
            "username": user.get("username") if not isAnonymous else "Anonymous",
            "userAvatar": user.get("profileImage") if not isAnonymous else None,
            "content": content if content else "",  # Allow empty content if image is present
            "storyType": storyType,
            "imageUrl": image_url,
            "isAnonymous": isAnonymous,
            "views": [],
            "createdAt": datetime.now(timezone.utc),
            "expiresAt": datetime.now(timezone.utc) + timedelta(hours=24)
        }
        
        await db.stories.insert_one(story)
        
        return {
            "success": True,
            "message": "Story created successfully",
            "story": {
                "id": story["id"],
                "expiresAt": story["expiresAt"].isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_router.get("/stories")
async def get_stories(userId: str, skip: int = 0, limit: int = 50):
    """Get active stories (not expired)"""
    try:
        # Get non-expired stories
        now = datetime.now(timezone.utc)
        
        stories = await db.stories.find({
            "expiresAt": {"$gt": now}
        }).sort("createdAt", -1).skip(skip).limit(limit).to_list(limit)
        
        # Format stories
        formatted_stories = []
        for story in stories:
            # Check if user viewed
            user_viewed = userId in story.get("views", [])
            
            formatted_stories.append({
                "id": story["id"],
                "userId": story.get("userId"),
                "username": story.get("username"),
                "userAvatar": story.get("userAvatar"),
                "content": story.get("content"),
                "storyType": story.get("storyType"),
                "imageUrl": story.get("imageUrl"),
                "isAnonymous": story.get("isAnonymous", False),
                "views": len(story.get("views", [])),
                "userViewed": user_viewed,
                "createdAt": story["createdAt"].isoformat(),
                "expiresAt": story["expiresAt"].isoformat(),
                "timeAgo": get_time_ago(story["createdAt"])
            })
        
        return {
            "success": True,
            "stories": formatted_stories
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_router.post("/stories/{storyId}/view")
async def view_story(storyId: str, userId: str = Form(...)):
    """Mark story as viewed"""
    try:
        story = await db.stories.find_one({"id": storyId})
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        views = story.get("views", [])
        
        if userId not in views:
            views.append(userId)
            await db.stories.update_one(
                {"id": storyId},
                {"$set": {"views": views}}
            )
        
        return {
            "success": True,
            "viewCount": len(views)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# FOLLOW SYSTEM

@social_router.post("/follow")
async def follow_user(userId: str = Form(...), targetUserId: str = Form(...)):
    """Follow a user"""
    try:
        if userId == targetUserId:
            raise HTTPException(status_code=400, detail="Cannot follow yourself")
        
        user = await db.users.find_one({"id": userId})
        target = await db.users.find_one({"id": targetUserId})
        
        if not user or not target:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Add to following list
        following = user.get("following", [])
        if targetUserId not in following:
            following.append(targetUserId)
            await db.users.update_one(
                {"id": userId},
                {"$set": {"following": following}}
            )
        
        # Add to followers list
        followers = target.get("followers", [])
        if userId not in followers:
            followers.append(userId)
            await db.users.update_one(
                {"id": targetUserId},
                {"$set": {"followers": followers}}
            )
        
        return {
            "success": True,
            "message": "Followed successfully",
            "following": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_router.post("/unfollow")
async def unfollow_user(userId: str = Form(...), targetUserId: str = Form(...)):
    """Unfollow a user"""
    try:
        user = await db.users.find_one({"id": userId})
        target = await db.users.find_one({"id": targetUserId})
        
        if not user or not target:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove from following list
        following = user.get("following", [])
        if targetUserId in following:
            following.remove(targetUserId)
            await db.users.update_one(
                {"id": userId},
                {"$set": {"following": following}}
            )
        
        # Remove from followers list
        followers = target.get("followers", [])
        if userId in followers:
            followers.remove(userId)
            await db.users.update_one(
                {"id": targetUserId},
                {"$set": {"followers": followers}}
            )
        
        return {
            "success": True,
            "message": "Unfollowed successfully",
            "following": False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_router.get("/users/{userId}/followers")
async def get_followers(userId: str):
    """Get user's followers"""
    try:
        user = await db.users.find_one({"id": userId})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        follower_ids = user.get("followers", [])
        
        # Get follower details
        followers = []
        for fid in follower_ids:
            follower = await db.users.find_one({"id": fid})
            if follower:
                followers.append({
                    "id": follower["id"],
                    "username": follower.get("username"),
                    "fullName": follower.get("fullName"),
                    "profileImage": follower.get("profileImage"),
                    "bio": follower.get("bio", "")
                })
        
        return {
            "success": True,
            "followers": followers,
            "count": len(followers)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_router.get("/users/{userId}/following")
async def get_following(userId: str):
    """Get users that this user follows"""
    try:
        user = await db.users.find_one({"id": userId})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        following_ids = user.get("following", [])
        
        # Get following details
        following = []
        for fid in following_ids:
            followed_user = await db.users.find_one({"id": fid})
            if followed_user:
                following.append({
                    "id": followed_user["id"],
                    "username": followed_user.get("username"),
                    "fullName": followed_user.get("fullName"),
                    "profileImage": followed_user.get("profileImage"),
                    "bio": followed_user.get("bio", "")
                })
        
        return {
            "success": True,
            "following": following,
            "count": len(following)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# UTILITY FUNCTIONS

def get_time_ago(dt):
    """Convert datetime to 'time ago' format"""
    # Ensure dt is timezone-aware
    if dt.tzinfo is None:
        from datetime import timezone as tz
        dt = dt.replace(tzinfo=tz.utc)
    
    now = datetime.now(timezone.utc)
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days}d ago"
    else:
        weeks = int(seconds / 604800)
        return f"{weeks}w ago"
