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
import os
import logging
from uuid import uuid4

# Import PostgreSQL-backed MongoDB compatibility layer
from mongo_compat import db

# Setup logger
logger = logging.getLogger(__name__)

# Create router
social_router = APIRouter(prefix="/api/social", tags=["social"])

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
        user = await db.users.find_one({"id": userId})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        media_url = None
        image_url = None
        media_type = "image"

        if image:
            upload_dir = "/app/uploads/posts"
            os.makedirs(upload_dir, exist_ok=True)

            # Extract extension (default to .jpg if none)
            import os as _os
            original_name = image.filename or ""
            _, ext = _os.path.splitext(original_name)
            file_ext = ext.lstrip(".").lower() or "jpg"
            filename = f"{uuid4()}.{file_ext}"
            file_path = _os.path.join(upload_dir, filename)

            with open(file_path, "wb") as f:
                content_bytes = await image.read()
                f.write(content_bytes)

            # Return /api/uploads path for frontend
            media_url = f"/api/uploads/posts/{filename}"
            image_url = media_url

            if file_ext in ["mp4", "mov", "avi", "mkv", "webm"]:
                media_type = "video"

        # Don't set id manually - let PostgreSQL auto-generate it
        post_data = {
            "userId": userId if not isAnonymous else "anonymous",
            "username": user.get("username") if not isAnonymous else "Anonymous",
            "userAvatar": user.get("profileImage") if not isAnonymous else None,
            "userProfileImage": user.get("profileImage") if not isAnonymous else None,
            "content": content if content else "",
            "caption": content if content else "",  # Add caption field for frontend compatibility
            "postType": postType,
            "mediaUrl": media_url,
            "mediaType": media_type,
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

        # Insert and get the database-generated ID
        insert_result = await db.posts.insert_one(post_data)
        post_id = insert_result.get('inserted_id')

        return {
            "success": True,
            "message": "Post created successfully",
            "post": {
                # Return integer ID as string for frontend
                "id": str(post_id),
                "createdAt": post_data["createdAt"].isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_router.get("/posts/{postId}")
async def get_post_detail(postId: str, userId: Optional[str] = None):
    """
    Return detailed post data including like/comment counts and flags.
    """
    try:
        post_id_int = int(postId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    post = await db.posts.find_one({"id": post_id_int})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Normalize likes and remove duplicates
    raw_likes = post.get("likes", [])
    if isinstance(raw_likes, str):
        try:
            import json as _json
            raw_likes = _json.loads(raw_likes)
        except Exception:
            raw_likes = []
    normalized_likes = []
    for l in raw_likes:
        try:
            uid = int(l)
        except (ValueError, TypeError):
            uid = l
        if uid not in normalized_likes:
            normalized_likes.append(uid)
    like_count = len(normalized_likes)

    # Normalize comments and remove duplicates
    raw_comments = post.get("comments", [])
    if isinstance(raw_comments, str):
        try:
            import json as _json
            raw_comments = _json.loads(raw_comments)
        except Exception:
            raw_comments = []
    unique_comments = []
    seen_ids = set()
    for c in raw_comments:
        cid = c.get("id") if isinstance(c, dict) else None
        if cid and cid not in seen_ids:
            seen_ids.add(cid)
            unique_comments.append(c)
    comment_count = len(unique_comments)

    # Determine if current user liked this post
    try:
        user_id_int = int(userId) if userId else None
    except (ValueError, TypeError):
        user_id_int = userId
    user_liked = (user_id_int in normalized_likes) if userId else False

    # Get post author info
    post_author = await db.users.find_one({"id": post.get("userId")})
    
    return {
        "id": str(post["id"]),
        "userId": str(post.get("userId")),
        "username": post.get("username"),
        "userProfileImage": post_author.get("profileImage") if post_author else None,
        "content": post.get("content"),
        "caption": post.get("caption") or post.get("content"),
        "postType": post.get("postType"),
        "imageUrl": post.get("imageUrl") or post.get("mediaUrl"),
        "mediaUrl": post.get("mediaUrl"),
        "mediaType": post.get("mediaType", "image"),
        "likeCount": like_count,
        "commentCount": comment_count,
        "userLiked": user_liked,
        "likesHidden": post.get("likesHidden", False),
        "commentsDisabled": post.get("commentsDisabled", False),
        "createdAt": post["createdAt"].isoformat() if hasattr(post["createdAt"], 'isoformat') else post["createdAt"]
    }

@social_router.get("/feed")
async def get_feed(
    userId: str,
    page: int = 1,
    limit: int = 10,
    city: Optional[str] = None
):
    """Get feed with smart mix of new and unseen posts"""
    try:
        skip = (page - 1) * limit
        
        # Get user to check blockedUsers and mutedUsers
        current_user = await db.users.find_one({"id": userId})
        if not current_user:
            return {"success": False, "posts": []}
        
        blocked_users = current_user.get("blockedUsers", [])
        muted_users = current_user.get("mutedUsers", [])
        excluded_users = list(set(blocked_users + muted_users))
        
        # Build query to exclude blocked/muted users and own posts
        query = {
            "userId": {"$nin": excluded_users + [userId]}  # Exclude blocked, muted, and own posts
        }
        
        # Filter by city if provided
        if city:
            query["city"] = city
        
        # Get total posts count for this query
        total_posts = await db.posts.count_documents(query)
        
        # Smart algorithm: Mix of recent posts and older unseen posts
        # 70% recent posts, 30% older posts (randomized)
        recent_limit = int(limit * 0.7)
        older_limit = limit - recent_limit
        
        # Get recent posts
        recent_posts = await db.posts.find(query)\
            .sort("createdAt", -1)\
            .skip(skip)\
            .limit(recent_limit)\
            .to_list(recent_limit)
        
        # Get older posts (randomly sampled from earlier content)
        older_skip = skip + (page * 50)  # Skip further ahead for older content
        older_posts = await db.posts.find(query)\
            .sort("createdAt", -1)\
            .skip(older_skip)\
            .limit(older_limit)\
            .to_list(older_limit)
        
        # Merge and shuffle
        import random
        all_posts = recent_posts + older_posts
        random.shuffle(all_posts)
        
        # Format posts
        formatted_posts = []
        for post in all_posts:
            # Get post author's current profile picture, verification, and founder status
            post_author = await db.users.find_one(
                {"id": post.get("userId")}, 
                {"isVerified": 1, "isFounder": 1, "profileImage": 1}
            )
            is_verified = post_author.get("isVerified", False) if post_author else False
            is_founder = post_author.get("isFounder", False) if post_author else False
            current_profile_image = post_author.get("profileImage") if post_author else post.get("userAvatar")
            
            # Parse likes: handle JSON strings and remove duplicates
            raw_likes = post.get("likes", [])
            if isinstance(raw_likes, str):
                try:
                    import json as _json
                    parsed_likes = _json.loads(raw_likes)
                except Exception:
                    parsed_likes = []
            else:
                parsed_likes = raw_likes or []
            
            # Normalize to integers and remove duplicates
            normalized_likes = []
            for l in parsed_likes:
                try:
                    uid = int(l)
                except (ValueError, TypeError):
                    uid = l
                if uid not in normalized_likes:
                    normalized_likes.append(uid)
            like_count = len(normalized_likes)
            
            # Parse comments: handle JSON strings and remove duplicates by comment ID
            raw_comments = post.get("comments", [])
            if isinstance(raw_comments, str):
                try:
                    import json as _json
                    parsed_comments = _json.loads(raw_comments)
                except Exception:
                    parsed_comments = []
            else:
                parsed_comments = raw_comments or []
            
            # Remove duplicate comments by ID
            unique_comments = []
            seen_comment_ids = set()
            for c in parsed_comments:
                if isinstance(c, dict):
                    cid = c.get("id")
                    if cid and cid not in seen_comment_ids:
                        seen_comment_ids.add(cid)
                        unique_comments.append(c)
                else:
                    unique_comments.append(c)
            comment_count = len(unique_comments)
            
            # Check if current user liked (using normalized likes)
            try:
                user_id_int = int(userId)
            except (ValueError, TypeError):
                user_id_int = userId
            user_liked = user_id_int in normalized_likes
            
            formatted_posts.append({
                "id": str(post["id"]),  # Convert integer ID to string for frontend
                "userId": post.get("userId"),
                "username": post.get("username"),
                "userAvatar": current_profile_image,  # Use current profile picture
                "isVerified": is_verified,
                "isFounder": is_founder,
                "content": post.get("content"),
                "caption": post.get("caption") or post.get("content"),  # Add caption field for Instagram-style display
                "postType": post.get("postType"),
                "imageUrl": post.get("imageUrl") or post.get("mediaUrl"),  # Fallback to mediaUrl if imageUrl not present
                "isAnonymous": post.get("isAnonymous", False),
                # Support both old and new field names for frontend compatibility
                "likes": like_count,
                "comments": comment_count,
                "likeCount": like_count,
                "commentCount": comment_count,
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
        # Convert postId and userId to integers for PostgreSQL lookup
        try:
            post_id_int = int(postId)
            user_id_int = int(userId)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format")
        
        post = await db.posts.find_one({"id": post_id_int})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        likes = post.get("likes", [])
        
        # Normalize likes to list of integers
        if isinstance(likes, str):
            try:
                import json
                likes = json.loads(likes)
            except:
                likes = []
        likes = [int(l) if isinstance(l, str) else l for l in likes]
        
        if user_id_int in likes:
            # Unlike
            likes.remove(user_id_int)
            action = "unliked"
        else:
            # Like
            likes.append(user_id_int)
            action = "liked"
        
        # Update post
        await db.posts.update_one(
            {"id": post_id_int},
            {"$set": {"likes": likes}}
        )
        
        return {
            "success": True,
            "action": action,
            "likeCount": len(likes)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@social_router.post("/posts/{postId}/comment")
async def add_comment(
    postId: str,
    userId: str = Form(...),
    content: str = Form(...),
    isAnonymous: bool = Form(False),
    parentCommentId: Optional[str] = Form(None)
):
    """Add comment or reply to a post"""
    try:
        # Convert postId and userId to integers for PostgreSQL lookup
        try:
            post_id_int = int(postId)
            user_id_int = int(userId)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format")
        
        post = await db.posts.find_one({"id": post_id_int})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        user = await db.users.find_one({"id": user_id_int})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # If it's a reply, validate parent comment exists
        if parentCommentId:
            comments_list = post.get("comments", [])
            if isinstance(comments_list, str):
                try:
                    import json
                    comments_list = json.loads(comments_list)
                except:
                    comments_list = []
            parent_exists = any(c.get("id") == parentCommentId for c in comments_list)
            if not parent_exists:
                raise HTTPException(status_code=404, detail="Parent comment not found")
        
        # UNIFIED COMMENT FORMAT - matches /api/posts endpoint
        comment = {
            "id": str(uuid4()),
            "userId": str(user_id_int) if not isAnonymous else "anonymous",
            "username": user.get("username") if not isAnonymous else "Anonymous",
            "userProfileImage": user.get("profileImage") if not isAnonymous else None,  # Changed from userAvatar
            "text": content,  # Changed from content to text
            "createdAt": datetime.now(timezone.utc).isoformat(),  # Changed to isoformat string
            "isAnonymous": isAnonymous,
            "parentCommentId": parentCommentId,
            "likes": [],
            "likesCount": 0  # Added likesCount
        }
        
        # Get current comments and append new comment (FIXED: use $set instead of $push for PostgreSQL)
        post_comments = post.get("comments", [])
        if isinstance(post_comments, str):
            try:
                import json
                post_comments = json.loads(post_comments)
            except:
                post_comments = []
        
        post_comments.append(comment)
        
        # Add comment to post using $set instead of $push
        await db.posts.update_one(
            {"id": post_id_int},
            {"$set": {"comments": post_comments}}
        )
        
        # Create notification for post owner (if not commenting on own post and not anonymous)
        if not isAnonymous and post.get("userId") != user_id_int:
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
            "comment": comment  # Return full comment object with all fields
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get comments for a post
@social_router.get("/posts/{postId}/comments")
async def get_post_comments(postId: str, userId: Optional[str] = None):
    """Get all comments for a post with nested replies"""
    try:
        # Convert postId to integer for PostgreSQL lookup
        try:
            post_id_int = int(postId)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid post ID format")
        
        post = await db.posts.find_one({"id": post_id_int})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Parse comments - handle both JSON strings and objects
        raw_comments = post.get("comments", [])
        if isinstance(raw_comments, str):
            try:
                import json as _json
                comments = _json.loads(raw_comments)
            except Exception:
                comments = []
        else:
            comments = raw_comments if isinstance(raw_comments, list) else []
        
        # Organize comments and replies
        comment_map = {}
        root_comments = []
        
        for comment in comments:
            # Skip if comment is not a dict
            if not isinstance(comment, dict):
                continue
                
            comment_id = comment.get("id")
            likes = comment.get("likes", [])
            user_liked = userId in likes if userId else False
            
            # UNIFIED FORMAT - use same fields as /api/posts endpoint
            comment_data = {
                "id": comment_id,
                "userId": comment.get("userId"),
                "username": comment.get("username"),
                "userProfileImage": comment.get("userProfileImage", comment.get("userAvatar")),  # Support both
                "text": comment.get("text", comment.get("content")),  # Support both
                "createdAt": comment.get("createdAt"),
                "timeAgo": get_time_ago(comment.get("createdAt")),
                "likesCount": len(likes),
                "likes": likes,
                "userLiked": user_liked,
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
            
            # Construct the image URL using the API uploads route. Because
            # api_router uses a prefix of /api, stories are served from
            # /api/uploads/.... Including /api here ensures the URL
            # resolves correctly in both preview and production environments.
            image_url = f"/api/uploads/stories/{filename}"
        
        # Create story - don't set id manually, let PostgreSQL auto-generate it
        story_data = {
            "userId": userId if not isAnonymous else "anonymous",
            "username": user.get("username") if not isAnonymous else "Anonymous",
            "userAvatar": user.get("profileImage") if not isAnonymous else None,
            "content": content if content else "",  # Allow empty content if image is present
            "caption": content if content else "",  # Add caption field for compatibility
            "storyType": storyType,
            "imageUrl": image_url,
            "mediaUrl": image_url,  # Add mediaUrl for compatibility with /api/stories/feed
            "mediaType": storyType,  # Add mediaType for compatibility with /api/stories/feed
            "isAnonymous": isAnonymous,
            "views": [],
            "createdAt": datetime.now(timezone.utc),
            "expiresAt": datetime.now(timezone.utc) + timedelta(hours=24)
        }
        
        # Insert and get database-generated ID
        insert_result = await db.stories.insert_one(story_data)
        story_id = insert_result.get('inserted_id')
        
        return {
            "success": True,
            "message": "Story created successfully",
            "story": {
                "id": str(story_id),  # Return integer ID as string
                "expiresAt": story_data["expiresAt"].isoformat()
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
            # Get story author's current profile picture, verification, and founder status
            story_author = await db.users.find_one(
                {"id": story.get("userId")}, 
                {"isVerified": 1, "isFounder": 1, "profileImage": 1}
            )
            is_verified = story_author.get("isVerified", False) if story_author else False
            is_founder = story_author.get("isFounder", False) if story_author else False
            current_profile_image = story_author.get("profileImage") if story_author else story.get("userAvatar")
            
            # Check if user viewed
            user_viewed = userId in story.get("views", [])
            
            formatted_stories.append({
                "id": story["id"],
                "userId": story.get("userId"),
                "username": story.get("username"),
                "userAvatar": current_profile_image,  # Use current profile picture
                "isVerified": is_verified,
                "isFounder": is_founder,
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
    """Convert datetime to 'time ago' format - handles both datetime objects and ISO strings"""
    # Handle string input (PostgreSQL migration fix)
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except Exception:
            # If parsing fails, use current time as fallback
            dt = datetime.now(timezone.utc)
    
    # Handle None/NULL values from migration
    if dt is None:
        dt = datetime.now(timezone.utc)
    
    # Ensure dt is timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
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
