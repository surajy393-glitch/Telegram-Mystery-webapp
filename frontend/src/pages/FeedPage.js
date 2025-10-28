import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { Heart, MessageCircle, Share2, Send, Image as ImageIcon, Plus, Bell, Search, User } from 'lucide-react';
import CommentModal from '../components/CommentModal';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const FeedPage = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [newPost, setNewPost] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [commentingOn, setCommentingOn] = useState(null);
  const [commentText, setCommentText] = useState('');
  const [notificationCount, setNotificationCount] = useState(0);
  const [showCreateStory, setShowCreateStory] = useState(false);
  const [myStories, setMyStories] = useState(null);
  const [otherStories, setOtherStories] = useState([]);
  const [showStoryViewer, setShowStoryViewer] = useState(false);
  const [viewingStories, setViewingStories] = useState(null);
  const [currentStoryIndex, setCurrentStoryIndex] = useState(0);
  const [newStory, setNewStory] = useState({ mediaUrl: "", caption: "", mediaType: "image", mediaFile: null });
  const [showCommentModal, setShowCommentModal] = useState(false);
  const [selectedPost, setSelectedPost] = useState(null);

  useEffect(() => {
    if (user) {
      fetchFeed();
      fetchNotificationCount();
      fetchStories();
      
      // Poll notification count every 30 seconds
      const interval = setInterval(fetchNotificationCount, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const fetchNotificationCount = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API_URL}/api/notifications/unread-count`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotificationCount(response.data.count);
    } catch (error) {
      console.error("Error fetching notification count:", error);
    }
  };

  const fetchStories = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/social/stories?userId=${user.id}`);
      
      const stories = response.data.stories || [];
      
      // Group stories by user
      const storyGroups = {};
      stories.forEach(story => {
        const userId = story.userId;
        if (!storyGroups[userId]) {
          storyGroups[userId] = {
            userId: userId,
            username: story.username,
            userProfileImage: story.userAvatar,
            stories: []
          };
        }
        storyGroups[userId].stories.push(story);
      });
      
      // Separate my stories from others
      const myStory = storyGroups[user.id] || null;
      const otherUserStories = Object.values(storyGroups).filter(g => g.userId !== user.id);
      
      setMyStories(myStory);
      setOtherStories(otherUserStories);
      
      console.log('✅ Fetched stories:', { myStory, otherCount: otherUserStories.length });
    } catch (error) {
      console.error("Error fetching stories:", error);
    }
  };

  const fetchFeed = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/social/feed?userId=${user.id}&limit=20`);
      console.log('Feed response:', response.data);
      if (response.data.success) {
        console.log('Posts received:', response.data.posts);
        response.data.posts.forEach(post => {
          console.log(`Post ${post.id}: imageUrl = ${post.imageUrl}, postType = ${post.postType}`);
        });
        setPosts(response.data.posts);
      }
    } catch (error) {
      console.error('Error fetching feed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePost = async () => {
    // Allow posting with just image (no caption required)
    if (!newPost.trim() && !selectedImage) {
      alert('Please add some content or an image');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('content', newPost || 'Photo post');  // Default text if empty
      formData.append('userId', user.id);
      formData.append('postType', selectedImage ? 'image' : 'text');
      formData.append('isAnonymous', isAnonymous);
      
      if (selectedImage) {
        formData.append('image', selectedImage);
      }

      const response = await axios.post(`${API_URL}/api/social/posts`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (response.data.success) {
        setNewPost('');
        setSelectedImage(null);
        setIsAnonymous(false);
        setShowCreatePost(false);
        fetchFeed();
      }
    } catch (error) {
      console.error('Error creating post:', error);
      alert('Failed to create post');
    }
  };

  const handleLike = async (postId) => {
    try {
      const formData = new FormData();
      formData.append('userId', user.id);
      
      const response = await axios.post(`${API_URL}/api/social/posts/${postId}/like`, formData);
      
      if (response.data.success) {
        // Update local state
        setPosts(posts.map(post => 
          post.id === postId 
            ? { 
                ...post, 
                userLiked: !post.userLiked, 
                likes: response.data.likeCount 
              }
            : post
        ));
      }
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  const handleComment = async (postId) => {
    if (!commentText.trim()) return;

    try {
      const formData = new FormData();
      formData.append('userId', user.id);
      formData.append('content', commentText);
      formData.append('isAnonymous', false);

      const response = await axios.post(`${API_URL}/api/social/posts/${postId}/comment`, formData);

      if (response.data.success) {
        setCommentText('');
        setCommentingOn(null);
        // Refresh post to show new comment
        fetchFeed();
      }
    } catch (error) {
      console.error('Error commenting:', error);
    }
  };

  const openStoryViewer = (storyGroup) => {
    setViewingStories(storyGroup);
    setCurrentStoryIndex(0);
    setShowStoryViewer(true);
  };

  const handleStoryImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Store the actual file object
      setNewStory({ 
        ...newStory, 
        mediaFile: file,
        mediaUrl: URL.createObjectURL(file), // For preview
        mediaType: file.type.startsWith("video") ? "video" : "image" 
      });
    }
  };

  const handleCreateStory = async () => {
    if (!newStory.mediaFile) {
      alert('Please select an image or video');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('userId', user.id);
      formData.append('content', newStory.caption || '');
      formData.append('storyType', newStory.mediaType);
      formData.append('isAnonymous', false);
      formData.append('image', newStory.mediaFile); // Send the actual file

      const response = await axios.post(`${API_URL}/api/social/stories`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (response.data.success) {
        setNewStory({ mediaUrl: "", caption: "", mediaType: "image", mediaFile: null });
        setShowCreateStory(false);
        fetchStories();
        alert('Story created successfully!');
      }
    } catch (error) {
      console.error('Error creating story:', error);
      console.error('Error response:', error.response?.data);
      alert('Failed to create story: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleShare = async (post) => {
    const shareUrl = `${window.location.origin}/post/${post.id}`;
    const shareText = `Check out this post by ${post.username} on LuvHive!`;

    try {
      // Try native share API (works on mobile)
      if (navigator.share) {
        await navigator.share({
          title: 'LuvHive Post',
          text: shareText,
          url: shareUrl
        });
      } else {
        // Fallback: Copy to clipboard
        await navigator.clipboard.writeText(shareUrl);
        alert('Link copied to clipboard!');
      }
    } catch (error) {
      // If share cancelled or failed, try clipboard
      try {
        await navigator.clipboard.writeText(shareUrl);
        alert('Link copied to clipboard!');
      } catch (err) {
        console.error('Error sharing:', err);
        alert('Unable to share. Link: ' + shareUrl);
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-2xl mx-auto px-4 py-3">
          {/* Top row with logo and icons */}
          <div className="flex items-center justify-between mb-3">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
              LuvHive
            </h1>
            <div className="flex items-center gap-2">
              {/* Mystery Button */}
              <button
                onClick={() => navigate('/mystery')}
                className="px-3 py-1.5 rounded-full bg-gradient-to-r from-purple-400 to-indigo-400 text-white text-sm font-medium flex items-center gap-1.5 hover:from-purple-500 hover:to-indigo-500 transition-all shadow-md"
              >
                <span className="text-base">🎭</span>
                <span className="hidden sm:inline">Mystery</span>
              </button>
              
              <Link to="/notifications">
                <button className="relative p-2 hover:bg-gray-100 rounded-full transition-colors">
                  <Bell className="w-5 h-5 text-gray-700" />
                  {notificationCount > 0 && (
                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                      {notificationCount}
                    </span>
                  )}
                </button>
              </Link>
              <Link to="/search">
                <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                  <Search className="w-5 h-5 text-gray-700" />
                </button>
              </Link>
              <button
                onClick={() => navigate('/my-profile')}
                className="w-9 h-9 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center text-white text-sm font-semibold hover:shadow-lg transition-all"
              >
                {user?.username?.[0]?.toUpperCase()}
              </button>
            </div>
          </div>
          
          {/* Bottom row with stories horizontal scroll */}
          <div className="flex items-center gap-3">
            {/* Stories Horizontal Scroll */}
            <div className="flex gap-3 overflow-x-auto scrollbar-hide flex-1">
              {/* User's Own Story - Add Story Button */}
              <div 
                className="flex-shrink-0 text-center cursor-pointer" 
                onClick={() => {
                  if (myStories) {
                    // Has stories - open viewer
                    openStoryViewer(myStories);
                  } else {
                    // No stories - open create dialog
                    setShowCreateStory(true);
                  }
                }}
              >
                <div className="relative">
                  <div className={`w-16 h-16 rounded-full p-0.5 ${myStories ? 'bg-gradient-to-br from-pink-500 to-rose-500' : 'bg-gray-300'}`}>
                    <div className="w-full h-full rounded-full bg-white p-0.5">
                      <img
                        src={
                          user?.profileImage 
                            ? (user.profileImage.startsWith('data:') || user.profileImage.startsWith('http') 
                                ? user.profileImage 
                                : `${API_URL}${user.profileImage}`)
                            : "https://via.placeholder.com/64"
                        }
                        alt="Your story"
                        className="w-full h-full rounded-full object-cover"
                        onError={(e) => e.target.src = "https://via.placeholder.com/64"}
                      />
                    </div>
                  </div>
                  {/* Plus icon for adding story - only show if no stories */}
                  <div 
                    className="absolute bottom-0 right-0 w-5 h-5 bg-gradient-to-br from-pink-500 to-rose-500 rounded-full flex items-center justify-center border-2 border-white cursor-pointer hover:scale-110 transition-transform"
                    onClick={(e) => {
                      e.stopPropagation(); // Prevent parent click
                      setShowCreateStory(true);
                    }}
                  >
                    <Plus className="w-3 h-3 text-white" />
                  </div>
                </div>
                <p className="text-xs mt-1 text-gray-700 font-medium truncate w-16">
                  {myStories ? 'Your Story' : 'Add Story'}
                </p>
              </div>

              {/* Other Users' Stories */}
              {otherStories.map((storyGroup) => (
                <div 
                  key={storyGroup.userId} 
                  className="flex-shrink-0 text-center cursor-pointer"
                  onClick={() => openStoryViewer(storyGroup)}
                >
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-pink-500 to-rose-500 p-0.5">
                    <div className="w-full h-full rounded-full bg-white p-0.5">
                      <img
                        src={storyGroup.userProfileImage || "https://via.placeholder.com/64"}
                        alt={storyGroup.username}
                        className="w-full h-full rounded-full object-cover"
                      />
                    </div>
                  </div>
                  <p className="text-xs mt-1 text-gray-700 font-medium truncate w-16">
                    {storyGroup.username}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* Create Post Button */}
        <button
          onClick={() => setShowCreatePost(true)}
          className="w-full bg-white rounded-lg shadow-sm p-4 mb-6 flex items-center space-x-3 hover:shadow-md transition-shadow"
        >
          <div className="w-10 h-10 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center text-white">
            <Plus size={20} />
          </div>
          <span className="text-gray-500">What's on your mind?</span>
        </button>

        {/* Create Post Modal */}
        {showCreatePost && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-lg w-full p-6">
              <h2 className="text-xl font-bold mb-4">Create Post</h2>
              
              <textarea
                value={newPost}
                onChange={(e) => setNewPost(e.target.value)}
                placeholder="What's on your mind?"
                className="w-full border border-gray-300 rounded-lg p-3 mb-4 resize-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                rows="4"
              />

              {selectedImage && (
                <div className="mb-4 relative">
                  <img
                    src={URL.createObjectURL(selectedImage)}
                    alt="Preview"
                    className="w-full rounded-lg max-h-64 object-cover"
                  />
                  <button
                    onClick={() => setSelectedImage(null)}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-2 hover:bg-red-600"
                  >
                    ×
                  </button>
                </div>
              )}

              <div className="flex items-center justify-between mb-4">
                <label className="flex items-center space-x-2 cursor-pointer text-gray-600 hover:text-pink-600">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setSelectedImage(e.target.files[0])}
                    className="hidden"
                  />
                  <ImageIcon size={20} />
                  <span>Add Photo</span>
                </label>

                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isAnonymous}
                    onChange={(e) => setIsAnonymous(e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-600">Post Anonymously</span>
                </label>
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    setShowCreatePost(false);
                    setNewPost('');
                    setSelectedImage(null);
                  }}
                  className="flex-1 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreatePost}
                  disabled={!newPost.trim() && !selectedImage}
                  className="flex-1 py-2 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-lg hover:from-pink-600 hover:to-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Post
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Feed Posts */}
        {posts.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow-sm">
            <p className="text-gray-500 mb-4">No posts yet. Be the first to post!</p>
            <button
              onClick={() => setShowCreatePost(true)}
              className="px-6 py-2 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-lg"
            >
              Create First Post
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {posts.map((post) => (
              <div key={post.id} className="bg-white rounded-lg shadow-sm">
                {/* Post Header */}
                <div className="p-4 flex items-center space-x-3">
                  <img
                    src={
                      post.isAnonymous 
                        ? "https://via.placeholder.com/40?text=?" 
                        : (post.userAvatar 
                            ? (post.userAvatar.startsWith('data:') || post.userAvatar.startsWith('http') 
                                ? post.userAvatar 
                                : `${API_URL}${post.userAvatar}`)
                            : "https://via.placeholder.com/40")
                    }
                    alt={post.username}
                    className="w-10 h-10 rounded-full object-cover border-2 border-gray-200"
                    onError={(e) => e.target.src = "https://via.placeholder.com/40"}
                  />
                  <div>
                    <h3 
                      className="font-semibold cursor-pointer hover:text-pink-600 transition-colors"
                      onClick={async () => {
                        if (post.isAnonymous) return;
                        
                        // Check if user profile is private
                        try {
                          const response = await axios.get(`${API_URL}/api/users/${post.userId}`);
                          if (response.data.isPrivate && response.data.id !== user.id) {
                            alert('This account is private');
                          } else {
                            navigate(`/profile/${post.userId}`);
                          }
                        } catch (error) {
                          console.error('Error checking profile:', error);
                          navigate(`/profile/${post.userId}`);
                        }
                      }}
                    >
                      {post.isAnonymous ? 'Anonymous' : post.username}
                    </h3>
                    <p className="text-xs text-gray-500">{post.timeAgo}</p>
                  </div>
                </div>

                {/* Post Content */}
                {post.content && post.content.trim() && post.content !== 'Photo post' && (
                  <div className="px-4 pb-3">
                    <p className="text-gray-800">{post.content}</p>
                  </div>
                )}

                {/* Post Image - FIXED VERSION */}
                {post.imageUrl ? (
                  <div className="w-full">
                    <img
                      src={post.imageUrl.startsWith('data:') || post.imageUrl.startsWith('http') 
                        ? post.imageUrl 
                        : `${API_URL}${post.imageUrl}`}
                      alt="Post"
                      className="w-full max-h-96 object-cover"
                      onLoad={() => console.log('✅ Image loaded:', post.imageUrl)}
                      onError={(e) => {
                        console.error('❌ Image failed:', post.imageUrl);
                        console.error('Full URL tried:', e.target.src);
                      }}
                    />
                  </div>
                ) : null}

                {/* Post Actions */}
                <div className="px-4 py-3 flex items-center justify-between border-t border-gray-100">
                  <button
                    onClick={() => handleLike(post.id)}
                    className={`flex items-center space-x-2 ${
                      post.userLiked ? 'text-pink-600' : 'text-gray-600'
                    } hover:text-pink-600`}
                  >
                    <Heart size={20} fill={post.userLiked ? 'currentColor' : 'none'} />
                    <span>{post.likes}</span>
                  </button>

                  <button
                    onClick={() => {
                      setSelectedPost(post);
                      setShowCommentModal(true);
                    }}
                    className="flex items-center space-x-2 text-gray-600 hover:text-pink-600"
                  >
                    <MessageCircle size={20} />
                    <span>{post.comments}</span>
                  </button>

                  <button 
                    onClick={() => handleShare(post)}
                    className="flex items-center space-x-2 text-gray-600 hover:text-pink-600"
                  >
                    <Share2 size={20} />
                  </button>
                </div>

                {/* Comment Input */}
                {commentingOn === post.id && (
                  <div className="px-4 pb-4 flex items-center space-x-2 border-t border-gray-100 pt-3">
                    <input
                      type="text"
                      value={commentText}
                      onChange={(e) => setCommentText(e.target.value)}
                      placeholder="Write a comment..."
                      className="flex-1 border border-gray-300 rounded-full px-4 py-2 focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          handleComment(post.id);
                        }
                      }}
                    />
                    <button
                      onClick={() => handleComment(post.id)}
                      className="p-2 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full hover:from-pink-600 hover:to-purple-600"
                    >
                      <Send size={18} />
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Story Modal */}
      {showCreateStory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-lg w-full p-6">
            <h2 className="text-xl font-bold mb-4">Add to Your Story</h2>
            
            {newStory.mediaUrl && (
              <div className="mb-4 relative">
                {newStory.mediaType === "video" ? (
                  <video
                    src={newStory.mediaUrl}
                    controls
                    className="w-full rounded-lg max-h-64 object-cover"
                  />
                ) : (
                  <img
                    src={newStory.mediaUrl}
                    alt="Preview"
                    className="w-full rounded-lg max-h-64 object-cover"
                  />
                )}
                <button
                  onClick={() => setNewStory({ ...newStory, mediaUrl: "" })}
                  className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-2 hover:bg-red-600"
                >
                  ×
                </button>
              </div>
            )}

            {!newStory.mediaUrl && (
              <label className="block border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-pink-500">
                <ImageIcon className="mx-auto mb-2 text-gray-400" size={48} />
                <span className="text-gray-600">Click to select image or video</span>
                <input
                  type="file"
                  accept="image/*,video/*"
                  onChange={handleStoryImageUpload}
                  className="hidden"
                />
              </label>
            )}

            <textarea
              value={newStory.caption}
              onChange={(e) => setNewStory({ ...newStory, caption: e.target.value })}
              placeholder="Add a caption (optional)"
              className="w-full border border-gray-300 rounded-lg p-3 mb-4 mt-4 resize-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
              rows="2"
            />

            <div className="flex space-x-2">
              <button
                onClick={() => {
                  setShowCreateStory(false);
                  setNewStory({ mediaUrl: "", caption: "", mediaType: "image" });
                }}
                className="flex-1 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateStory}
                disabled={!newStory.mediaUrl}
                className="flex-1 py-2 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-lg hover:from-pink-600 hover:to-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Add Story
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Story Viewer */}
      {showStoryViewer && viewingStories && (
        <div className="fixed inset-0 bg-black z-50 flex items-center justify-center">
          <button
            onClick={() => {
              setShowStoryViewer(false);
              setViewingStories(null);
              setCurrentStoryIndex(0);
            }}
            className="absolute top-4 right-4 text-white text-4xl z-20 w-12 h-12 flex items-center justify-center hover:bg-white/20 rounded-full transition-colors"
          >
            ×
          </button>
          
          <div className="relative w-full max-w-md h-full flex flex-col">
            {/* Story Header */}
            <div className="absolute top-0 left-0 right-0 z-10 p-4 bg-gradient-to-b from-black/70 to-transparent">
              <div className="flex items-center space-x-3">
                <img
                  src={viewingStories.userProfileImage || "https://via.placeholder.com/40"}
                  alt={viewingStories.username}
                  className="w-10 h-10 rounded-full border-2 border-white"
                />
                <div>
                  <h3 className="text-white font-semibold">{viewingStories.username}</h3>
                  <p className="text-white text-xs opacity-75">
                    {new Date(viewingStories.stories[currentStoryIndex]?.createdAt).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Story Content */}
            <div className="flex-1 flex items-center justify-center">
              {viewingStories.stories[currentStoryIndex]?.storyType === "video" ? (
                <video
                  src={
                    viewingStories.stories[currentStoryIndex]?.imageUrl 
                      ? `${API_URL}${viewingStories.stories[currentStoryIndex].imageUrl}`
                      : "https://via.placeholder.com/400"
                  }
                  controls
                  autoPlay
                  className="max-w-full max-h-full object-contain"
                  onError={(e) => {
                    console.error('Story video failed:', viewingStories.stories[currentStoryIndex]?.imageUrl);
                  }}
                />
              ) : (
                <img
                  src={
                    viewingStories.stories[currentStoryIndex]?.imageUrl 
                      ? `${API_URL}${viewingStories.stories[currentStoryIndex].imageUrl}`
                      : "https://via.placeholder.com/400"
                  }
                  alt="Story"
                  className="max-w-full max-h-full object-contain"
                  onLoad={() => console.log('✅ Story image loaded')}
                  onError={(e) => {
                    console.error('❌ Story image failed:', viewingStories.stories[currentStoryIndex]?.imageUrl);
                    e.target.src = "https://via.placeholder.com/400?text=Image+Not+Found";
                  }}
                />
              )}
            </div>

            {/* Navigation */}
            {viewingStories.stories.length > 1 && (
              <>
                {currentStoryIndex > 0 && (
                  <button
                    onClick={() => setCurrentStoryIndex(currentStoryIndex - 1)}
                    className="absolute left-4 top-1/2 transform -translate-y-1/2 w-12 h-12 flex items-center justify-center bg-black/50 hover:bg-black/70 text-white text-4xl rounded-full transition-all shadow-lg"
                  >
                    ‹
                  </button>
                )}
                {currentStoryIndex < viewingStories.stories.length - 1 && (
                  <button
                    onClick={() => setCurrentStoryIndex(currentStoryIndex + 1)}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 w-12 h-12 flex items-center justify-center bg-black/50 hover:bg-black/70 text-white text-4xl rounded-full transition-all shadow-lg"
                  >
                    ›
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Comment Modal */}
      <CommentModal
        post={selectedPost}
        user={user}
        isOpen={showCommentModal}
        onClose={() => {
          setShowCommentModal(false);
          setSelectedPost(null);
        }}
        onCommentAdded={fetchFeed}
      />
    </div>
  );
};

export default FeedPage;
