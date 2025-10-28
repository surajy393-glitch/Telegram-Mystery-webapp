import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Heart, MessageCircle, Send, Image as ImageIcon } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PostDetailPage = ({ user }) => {
  const { postId } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [replyingTo, setReplyingTo] = useState(null);
  const [replyText, setReplyText] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPostDetails();
    fetchComments();
  }, [postId]);

  const fetchPostDetails = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API}/posts/${postId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPost(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching post:", error);
      setLoading(false);
    }
  };

  const fetchComments = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API}/posts/${postId}/comments`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setComments(response.data.comments || []);
    } catch (error) {
      console.error("Error fetching comments:", error);
      setComments([]);
    }
  };

  const handleLike = async () => {
    if (!post) return;
    
    try {
      const token = localStorage.getItem("token");
      const isLiked = post.userLiked;
      const endpoint = isLiked ? 'unlike' : 'like';
      
      // Optimistic update
      setPost(prev => ({
        ...prev,
        userLiked: !isLiked,
        likesCount: isLiked ? Math.max(0, prev.likesCount - 1) : prev.likesCount + 1
      }));

      await axios.post(`${API}/posts/${postId}/${endpoint}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    } catch (error) {
      console.error("Error liking post:", error);
      // Rollback on error
      setPost(prev => ({
        ...prev,
        userLiked: !prev.userLiked,
        likesCount: prev.userLiked ? prev.likesCount + 1 : Math.max(0, prev.likesCount - 1)
      }));
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    try {
      const token = localStorage.getItem("token");
      const formData = new FormData();
      formData.append('text', newComment);
      
      const response = await axios.post(
        `${API}/posts/${postId}/comment`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Add new comment to list
      setComments(prev => [...prev, response.data.comment]);
      
      // Update comment count
      setPost(prev => ({
        ...prev,
        commentsCount: prev.commentsCount + 1
      }));

      setNewComment("");
    } catch (error) {
      console.error("Error adding comment:", error);
      alert("Failed to add comment");
    }
  };

  const handleLikeComment = async (commentId) => {
    try {
      const token = localStorage.getItem("token");
      
      // Optimistic update
      setComments(prev => prev.map(comment => {
        if (comment.id === commentId) {
          const likes = comment.likes || [];
          const userLiked = likes.includes(user.id);
          return {
            ...comment,
            likes: userLiked 
              ? likes.filter(id => id !== user.id)
              : [...likes, user.id],
            likesCount: userLiked ? (comment.likesCount || 0) - 1 : (comment.likesCount || 0) + 1
          };
        }
        return comment;
      }));

      // Make API call - for now we'll update the post's comments array
      const response = await axios.post(
        `${API}/posts/${postId}/comment/${commentId}/like`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
    } catch (error) {
      console.error("Error liking comment:", error);
    }
  };

  const handleReply = async (commentId) => {
    if (!replyText.trim()) return;

    try {
      const token = localStorage.getItem("token");
      const formData = new FormData();
      formData.append('text', replyText);
      formData.append('parentCommentId', commentId);
      
      const response = await axios.post(
        `${API}/posts/${postId}/comment`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Add reply to comments list
      setComments(prev => [...prev, response.data.comment]);
      
      setReplyText("");
      setReplyingTo(null);
    } catch (error) {
      console.error("Error adding reply:", error);
      alert("Failed to add reply");
    }
  };

  const handleShare = async () => {
    const shareUrl = `${window.location.origin}/post/${postId}`;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Check out this post!',
          text: post?.caption || 'Check out this post on LuvHive',
          url: shareUrl
        });
      } catch (error) {
        console.log("Share cancelled");
      }
    } else {
      try {
        await navigator.clipboard.writeText(shareUrl);
        alert("Link copied to clipboard!");
      } catch (error) {
        alert("Failed to copy link");
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Post not found</p>
          <button
            onClick={() => navigate(-1)}
            className="text-pink-600 hover:text-pink-700 font-semibold"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50">
      {/* Header with Back Button */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-bold">Post</h1>
        </div>
      </div>

      {/* Post Content */}
      <div className="max-w-6xl mx-auto p-4">
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <div className="md:flex">
            {/* Post Image */}
            <div className="md:w-3/5 bg-black flex items-center justify-center">
              {post.imageUrl || post.mediaUrl ? (
                <img
                  src={post.imageUrl || `${BACKEND_URL}${post.mediaUrl}`}
                  alt={post.caption || "Post"}
                  className="w-full object-contain max-h-[80vh]"
                />
              ) : (
                <div className="w-full h-96 bg-gradient-to-br from-pink-100 to-purple-100 flex items-center justify-center">
                  <ImageIcon className="w-20 h-20 text-pink-300" />
                </div>
              )}
            </div>

            {/* Post Details */}
            <div className="md:w-2/5 flex flex-col max-h-[80vh]">
              {/* User Info */}
              <div className="p-4 border-b">
                <div className="flex items-center gap-3">
                  {post.userProfileImage ? (
                    <img
                      src={`${BACKEND_URL}${post.userProfileImage}`}
                      alt={post.username}
                      className="w-10 h-10 rounded-full object-cover cursor-pointer"
                      onClick={() => navigate(`/profile/${post.userId}`)}
                      onError={(e) => e.target.src = "https://via.placeholder.com/40"}
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-pink-200 flex items-center justify-center text-pink-600 font-semibold">
                      {post.username?.[0]?.toUpperCase() || "U"}
                    </div>
                  )}
                  <span 
                    className="font-semibold text-gray-800 cursor-pointer hover:text-pink-600"
                    onClick={() => navigate(`/profile/${post.userId}`)}
                  >
                    {post.username}
                  </span>
                </div>
              </div>

              {/* Caption and Comments */}
              <div className="flex-1 overflow-y-auto p-4">
                {/* Caption */}
                {post.caption && (
                  <div className="flex gap-3 mb-6">
                    {post.userProfileImage ? (
                      <img
                        src={`${BACKEND_URL}${post.userProfileImage}`}
                        alt={post.username}
                        className="w-8 h-8 rounded-full object-cover"
                        onError={(e) => e.target.src = "https://via.placeholder.com/32"}
                      />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-pink-200 flex items-center justify-center text-pink-600 font-semibold text-sm">
                        {post.username?.[0]?.toUpperCase() || "U"}
                      </div>
                    )}
                    <div>
                      <span className="font-semibold mr-2">{post.username}</span>
                      <span className="text-gray-800">{post.caption}</span>
                    </div>
                  </div>
                )}

                {/* Comments */}
                <div className="space-y-4">
                  {comments.map((comment, idx) => (
                    <div key={idx} className="flex gap-3">
                      {comment.userProfileImage ? (
                        <img
                          src={`${BACKEND_URL}${comment.userProfileImage}`}
                          alt={comment.username}
                          className="w-8 h-8 rounded-full object-cover"
                          onError={(e) => e.target.src = "https://via.placeholder.com/32"}
                        />
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-pink-200 flex items-center justify-center text-pink-600 font-semibold text-sm">
                          {comment.username?.[0]?.toUpperCase() || "U"}
                        </div>
                      )}
                      <div className="flex-1">
                        <div>
                          <span className="font-semibold mr-2">{comment.username}</span>
                          <span className="text-gray-800">{comment.text}</span>
                        </div>
                        <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                          <span>{comment.createdAt ? new Date(comment.createdAt).toLocaleDateString() : 'Now'}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="p-4 border-t">
                <div className="flex items-center gap-4 mb-3">
                  <button 
                    onClick={handleLike}
                    className="hover:opacity-70 transition-opacity"
                  >
                    <Heart className={`w-7 h-7 ${post.userLiked ? 'fill-red-500 text-red-500' : ''}`} />
                  </button>
                  <button className="hover:opacity-70 transition-opacity">
                    <MessageCircle className="w-7 h-7" />
                  </button>
                  <button 
                    onClick={handleShare}
                    className="hover:opacity-70 transition-opacity"
                  >
                    <Send className="w-7 h-7" />
                  </button>
                </div>
                <p className="font-semibold text-sm mb-1">{post.likesCount || 0} likes</p>
                <p className="text-gray-500 text-xs mb-3">
                  {post.createdAt ? new Date(post.createdAt).toLocaleDateString() : 'Recently'}
                </p>

                {/* Add Comment Input */}
                <div className="flex items-center gap-2 border-t pt-3">
                  <input
                    type="text"
                    placeholder="Add a comment..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddComment()}
                    className="flex-1 outline-none text-sm"
                  />
                  <button
                    onClick={handleAddComment}
                    disabled={!newComment.trim()}
                    className={`text-sm font-semibold ${newComment.trim() ? 'text-pink-600 hover:text-pink-700' : 'text-gray-300'}`}
                  >
                    Post
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostDetailPage;
