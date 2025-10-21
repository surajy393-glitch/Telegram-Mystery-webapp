import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Heart, MessageCircle, Share2, Send, Image as ImageIcon, Plus } from 'lucide-react';

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

  useEffect(() => {
    if (user) {
      fetchFeed();
    }
  }, [user]);

  const fetchFeed = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/social/feed?userId=${user.id}&limit=20`);
      if (response.data.success) {
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
        <div className="max-w-2xl mx-auto px-4 py-3 flex items-center justify-between">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
            LuvHive
          </h1>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate('/stories')}
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-pink-500 to-purple-500 text-white font-semibold hover:from-pink-600 hover:to-purple-600 transition-all shadow-md"
            >
              📸 Stories
            </button>
            <button
              onClick={() => navigate('/mystery')}
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-indigo-500 text-white font-semibold hover:from-purple-600 hover:to-indigo-600 transition-all shadow-md"
            >
              🎭 Mystery
            </button>
            <button
              onClick={() => navigate('/my-profile')}
              className="w-10 h-10 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center text-white text-sm font-semibold hover:shadow-lg transition-all"
            >
              {user?.username?.[0]?.toUpperCase()}
            </button>
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
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center text-white">
                    {post.isAnonymous ? '?' : post.username?.[0]?.toUpperCase()}
                  </div>
                  <div>
                    <h3 className="font-semibold">
                      {post.isAnonymous ? 'Anonymous' : post.username}
                    </h3>
                    <p className="text-xs text-gray-500">{post.timeAgo}</p>
                  </div>
                </div>

                {/* Post Content */}
                {post.content && post.content.trim() && (
                  <div className="px-4 pb-3">
                    <p className="text-gray-800">{post.content}</p>
                  </div>
                )}

                {/* Post Image */}
                {post.imageUrl && (
                  <img
                    src={API_URL + post.imageUrl}
                    alt="Post"
                    className="w-full max-h-96 object-cover"
                  />
                )}

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
                    onClick={() => setCommentingOn(post.id)}
                    className="flex items-center space-x-2 text-gray-600 hover:text-pink-600"
                  >
                    <MessageCircle size={20} />
                    <span>{post.comments}</span>
                  </button>

                  <button className="flex items-center space-x-2 text-gray-600 hover:text-pink-600">
                    <Share2 size={20} />
                    <span>{post.shares}</span>
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
    </div>
  );
};

export default FeedPage;
