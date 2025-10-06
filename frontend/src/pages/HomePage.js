import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Heart, MessageCircle, Send, Plus, LogOut, User } from "lucide-react";
import axios from "axios";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HomePage = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [stories, setStories] = useState([]);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [showCreateStory, setShowCreateStory] = useState(false);
  const [newPost, setNewPost] = useState({ mediaUrl: "", caption: "", mediaType: "image" });
  const [newStory, setNewStory] = useState({ mediaUrl: "", caption: "", mediaType: "image" });

  useEffect(() => {
    fetchFeed();
  }, []);

  const fetchFeed = async () => {
    try {
      const token = localStorage.getItem("token");
      const headers = { Authorization: `Bearer ${token}` };

      const [storiesRes, postsRes] = await Promise.all([
        axios.get(`${API}/stories/feed`, { headers }),
        axios.get(`${API}/posts/feed`, { headers })
      ]);

      setStories(storiesRes.data.stories || []);
      setPosts(postsRes.data.posts || []);
    } catch (error) {
      console.error("Error fetching feed:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = (e, type) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        if (type === "post") {
          setNewPost({ ...newPost, mediaUrl: reader.result, mediaType: file.type.startsWith("video") ? "video" : "image" });
        } else {
          setNewStory({ ...newStory, mediaUrl: reader.result, mediaType: file.type.startsWith("video") ? "video" : "image" });
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCreatePost = async () => {
    if (!newPost.mediaUrl) {
      alert("Please upload an image or video");
      return;
    }

    try {
      const token = localStorage.getItem("token");
      await axios.post(`${API}/posts/create`, newPost, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setShowCreatePost(false);
      setNewPost({ mediaUrl: "", caption: "", mediaType: "image" });
      fetchFeed();
    } catch (error) {
      alert("Failed to create post");
    }
  };

  const handleCreateStory = async () => {
    if (!newStory.mediaUrl) {
      alert("Please upload an image or video");
      return;
    }

    try {
      const token = localStorage.getItem("token");
      await axios.post(`${API}/stories/create`, newStory, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setShowCreateStory(false);
      setNewStory({ mediaUrl: "", caption: "", mediaType: "image" });
      fetchFeed();
    } catch (error) {
      alert("Failed to create story");
    }
  };

  const handleLike = async (postId) => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(`${API}/posts/${postId}/like`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchFeed();
    } catch (error) {
      console.error("Error liking post:", error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-pink-50 to-white">
        <div className="text-2xl text-pink-600">Loading feed...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-pink-100" data-testid="home-page">
      {/* Header */}
      <header className="glass-effect sticky top-0 z-50 border-b border-pink-100">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-rose-500">
            LuvHive
          </h1>
          <div className="flex items-center gap-4">
            {user?.isPremium && (
              <span className="premium-badge">PREMIUM</span>
            )}
            <Link to="/profile">
              <Button variant="ghost" className="hover:bg-pink-50" data-testid="profile-btn">
                <User className="w-5 h-5 text-pink-600" />
              </Button>
            </Link>
            <Button 
              variant="ghost" 
              onClick={onLogout}
              className="hover:bg-pink-50"
              data-testid="logout-btn"
            >
              <LogOut className="w-5 h-5 text-pink-600" />
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6 max-w-2xl">
        {/* Stories Section */}
        <div className="mb-8 animate-fadeIn">
          <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
            {/* Add Story Button */}
            <div className="flex-shrink-0 text-center cursor-pointer" onClick={() => setShowCreateStory(true)}>
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-pink-400 to-rose-400 flex items-center justify-center border-4 border-white shadow-lg hover:scale-105 transition-transform">
                <Plus className="w-8 h-8 text-white" />
              </div>
              <p className="text-xs mt-2 text-gray-700 font-medium">Add Story</p>
            </div>

            {/* Stories */}
            {stories.map((storyGroup) => (
              <div key={storyGroup.userId} className="flex-shrink-0 text-center cursor-pointer">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-pink-500 to-rose-500 p-1 story-ring">
                  <div className="w-full h-full rounded-full bg-white p-1">
                    <img
                      src={storyGroup.userProfileImage || "https://via.placeholder.com/80"}
                      alt={storyGroup.username}
                      className="w-full h-full rounded-full object-cover"
                    />
                  </div>
                </div>
                <p className="text-xs mt-2 text-gray-700 font-medium truncate w-20">
                  {storyGroup.username}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Create Post Button */}
        <div className="mb-6">
          <Button
            onClick={() => setShowCreatePost(true)}
            data-testid="create-post-btn"
            className="w-full bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white py-6 rounded-2xl text-lg btn-hover"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create New Post
          </Button>
        </div>

        {/* Posts Feed */}
        <div className="space-y-6 animate-slideIn">
          {posts.length === 0 ? (
            <div className="text-center py-12 glass-effect rounded-3xl">
              <p className="text-gray-600 text-lg">No posts yet. Be the first to share!</p>
            </div>
          ) : (
            posts.map((post) => (
              <div key={post.id} className="glass-effect rounded-3xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow">
                {/* Post Header */}
                <div className="p-4 flex items-center gap-3">
                  <img
                    src={post.userProfileImage || "https://via.placeholder.com/40"}
                    alt={post.username}
                    className="w-10 h-10 rounded-full object-cover border-2 border-pink-200"
                  />
                  <div>
                    <p className="font-semibold text-gray-800">{post.username}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(post.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                {/* Post Media */}
                <div className="bg-gray-100">
                  {post.mediaType === "video" ? (
                    <video src={post.mediaUrl} controls className="w-full max-h-96 object-contain" />
                  ) : (
                    <img src={post.mediaUrl} alt="Post" className="w-full max-h-96 object-contain" />
                  )}
                </div>

                {/* Post Actions */}
                <div className="p-4">
                  <div className="flex gap-4 mb-3">
                    <button
                      onClick={() => handleLike(post.id)}
                      className="flex items-center gap-2 hover:scale-110 transition-transform"
                      data-testid={`like-btn-${post.id}`}
                    >
                      <Heart
                        className={`w-6 h-6 ${post.isLiked ? "fill-red-500 text-red-500" : "text-gray-700"}`}
                      />
                      <span className="text-sm text-gray-700">{post.likes.length}</span>
                    </button>
                    <button className="flex items-center gap-2 hover:scale-110 transition-transform">
                      <MessageCircle className="w-6 h-6 text-gray-700" />
                      <span className="text-sm text-gray-700">{post.comments.length}</span>
                    </button>
                  </div>

                  {/* Caption */}
                  {post.caption && (
                    <p className="text-gray-800">
                      <span className="font-semibold mr-2">{post.username}</span>
                      {post.caption}
                    </p>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Create Post Dialog */}
      <Dialog open={showCreatePost} onOpenChange={setShowCreatePost}>
        <DialogContent className="bg-white rounded-3xl" data-testid="create-post-dialog">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-rose-500">
              Create New Post
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 mt-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Image/Video
              </label>
              <input
                type="file"
                accept="image/*,video/*"
                onChange={(e) => handleImageUpload(e, "post")}
                className="w-full border border-gray-300 rounded-xl px-4 py-2"
              />
              {newPost.mediaUrl && (
                <div className="mt-4">
                  {newPost.mediaType === "video" ? (
                    <video src={newPost.mediaUrl} controls className="w-full rounded-xl max-h-64" />
                  ) : (
                    <img src={newPost.mediaUrl} alt="Preview" className="w-full rounded-xl max-h-64 object-contain" />
                  )}
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Caption (Optional)
              </label>
              <Textarea
                value={newPost.caption}
                onChange={(e) => setNewPost({ ...newPost, caption: e.target.value })}
                placeholder="Write a caption..."
                rows={3}
                className="border-gray-300 focus:border-pink-500 rounded-xl resize-none"
              />
            </div>
            <Button
              onClick={handleCreatePost}
              data-testid="submit-post-btn"
              className="w-full bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white py-4 rounded-xl btn-hover"
            >
              Post
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Create Story Dialog */}
      <Dialog open={showCreateStory} onOpenChange={setShowCreateStory}>
        <DialogContent className="bg-white rounded-3xl" data-testid="create-story-dialog">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-rose-500">
              Add to Your Story
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 mt-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Image/Video
              </label>
              <input
                type="file"
                accept="image/*,video/*"
                onChange={(e) => handleImageUpload(e, "story")}
                className="w-full border border-gray-300 rounded-xl px-4 py-2"
              />
              {newStory.mediaUrl && (
                <div className="mt-4">
                  {newStory.mediaType === "video" ? (
                    <video src={newStory.mediaUrl} controls className="w-full rounded-xl max-h-64" />
                  ) : (
                    <img src={newStory.mediaUrl} alt="Preview" className="w-full rounded-xl max-h-64 object-contain" />
                  )}
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Caption (Optional)
              </label>
              <Textarea
                value={newStory.caption}
                onChange={(e) => setNewStory({ ...newStory, caption: e.target.value })}
                placeholder="Add a caption..."
                rows={2}
                className="border-gray-300 focus:border-pink-500 rounded-xl resize-none"
              />
            </div>
            <Button
              onClick={handleCreateStory}
              data-testid="submit-story-btn"
              className="w-full bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white py-4 rounded-xl btn-hover"
            >
              Add Story
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default HomePage;
