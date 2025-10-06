import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Heart, MessageCircle, Send, Plus, LogOut, User as UserIcon, Bookmark, X, MoreVertical, Trash2, Download, Link2, Share2, AlertCircle } from "lucide-react";
import axios from "axios";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Utility function for relative time (IST-aware)
const getRelativeTime = (dateString) => {
  // Parse the UTC time from backend - ensure it's treated as UTC
  // If the string doesn't have 'Z' at end, add it to mark as UTC
  const utcString = dateString.endsWith('Z') ? dateString : dateString + 'Z';
  const postDate = new Date(utcString);
  const now = new Date();
  
  // Calculate difference in milliseconds
  const diffInMs = now.getTime() - postDate.getTime();
  const diffInSeconds = Math.floor(diffInMs / 1000);
  
  // Handle negative times (future dates - shouldn't happen but just in case)
  if (diffInSeconds < 0) {
    return "just now";
  }
  
  // Less than 1 minute
  if (diffInSeconds < 60) {
    return "just now";
  }
  
  // Less than 1 hour
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} min ago`;
  }
  
  // Less than 24 hours
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
  }
  
  // Less than 7 days
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
  }
  
  // More than 7 days - show date in IST
  return postDate.toLocaleDateString('en-IN', { 
    month: 'short', 
    day: 'numeric',
    year: postDate.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    timeZone: 'Asia/Kolkata'
  });
};

const HomePage = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [stories, setStories] = useState([]);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [showCreateStory, setShowCreateStory] = useState(false);
  const [showStoryViewer, setShowStoryViewer] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [storyToDelete, setStoryToDelete] = useState(null);
  const [viewingStories, setViewingStories] = useState(null);
  const [currentStoryIndex, setCurrentStoryIndex] = useState(0);
  const [showReportDialog, setShowReportDialog] = useState(false);
  const [reportingPost, setReportingPost] = useState(null);
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

  const handleSavePost = async (postId) => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(`${API}/posts/${postId}/save`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchFeed();
    } catch (error) {
      console.error("Error saving post:", error);
    }
  };

  const openStoryViewer = (storyGroup) => {
    setViewingStories(storyGroup);
    setCurrentStoryIndex(0);
    setShowStoryViewer(true);
  };

  const nextStory = () => {
    if (viewingStories && currentStoryIndex < viewingStories.stories.length - 1) {
      setCurrentStoryIndex(currentStoryIndex + 1);
    } else {
      setShowStoryViewer(false);
    }
  };

  const previousStory = () => {
    if (currentStoryIndex > 0) {
      setCurrentStoryIndex(currentStoryIndex - 1);
    }
  };

  const handleDeleteStory = async () => {
    if (!storyToDelete) return;

    try {
      const token = localStorage.getItem("token");
      await axios.delete(`${API}/stories/${storyToDelete}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setShowDeleteConfirm(false);
      setShowStoryViewer(false);
      setStoryToDelete(null);
      fetchFeed();
      alert("Story deleted successfully!");
    } catch (error) {
      alert("Failed to delete story");
    }
  };

  const handleSaveVideo = async () => {
    if (!viewingStories || !viewingStories.stories[currentStoryIndex]) return;

    const currentStory = viewingStories.stories[currentStoryIndex];
    const mediaUrl = currentStory.mediaUrl;

    try {
      // Download the media
      const link = document.createElement('a');
      link.href = mediaUrl;
      link.download = `story-${Date.now()}.${currentStory.mediaType === 'video' ? 'mp4' : 'jpg'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      alert("Media saved successfully!");
    } catch (error) {
      alert("Failed to save media");
    }
  };

  const handleCopyLink = () => {
    if (!viewingStories || !viewingStories.stories[currentStoryIndex]) return;

    const currentStory = viewingStories.stories[currentStoryIndex];
    const storyLink = `${window.location.origin}/story/${currentStory.id}`;

    navigator.clipboard.writeText(storyLink).then(() => {
      alert("Link copied to clipboard!");
    }).catch(() => {
      alert("Failed to copy link");
    });
  };

  const handleShareStory = async () => {
    if (!viewingStories || !viewingStories.stories[currentStoryIndex]) return;

    const currentStory = viewingStories.stories[currentStoryIndex];
    const storyLink = `${window.location.origin}/story/${currentStory.id}`;

    if (navigator.share) {
      try {
        await navigator.share({
          title: `Story by ${viewingStories.username}`,
          text: currentStory.caption || "Check out this story on LuvHive!",
          url: storyLink,
        });
      } catch (error) {
        if (error.name !== 'AbortError') {
          alert("Failed to share");
        }
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(storyLink).then(() => {
        alert("Link copied! Share it on Telegram, WhatsApp, Snapchat, or Instagram!");
      });
    }
  };

  const openDeleteConfirm = (storyId) => {
    setStoryToDelete(storyId);
    setShowDeleteConfirm(true);
  };

  const handleUnfollowFromPost = async (postUserId) => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(`${API}/users/${postUserId}/unfollow`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert("Unfollowed successfully!");
      fetchFeed(); // Refresh feed
    } catch (error) {
      console.error("Error unfollowing:", error);
      alert("Failed to unfollow");
    }
  };

  const handleReportPost = async (postId, reason) => {
    try {
      // In a real app, you'd send this to backend
      console.log(`Reporting post ${postId} for reason: ${reason}`);
      alert(`Post reported for: ${reason}\n\nThank you for helping keep LuvHive safe!`);
      setShowReportDialog(false);
      setReportingPost(null);
    } catch (error) {
      console.error("Error reporting post:", error);
    }
  };

  // Find user's own stories
  const myStories = stories.find(s => s.userId === user?.id);
  const otherStories = stories.filter(s => s.userId !== user?.id);

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
            <Link to="/my-profile">
              <Button variant="ghost" className="hover:bg-pink-50" data-testid="my-profile-btn">
                <UserIcon className="w-5 h-5 text-pink-600" />
              </Button>
            </Link>
            <Link to="/profile">
              <Button variant="ghost" className="hover:bg-pink-50 text-sm text-gray-600">
                Discover
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
            {/* User's Own Story */}
            <div className="flex-shrink-0 text-center cursor-pointer relative" data-testid="my-story-circle">
              {myStories ? (
                <div className="relative" onClick={() => openStoryViewer(myStories)}>
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-pink-500 to-rose-500 p-1 story-ring">
                    <div className="w-full h-full rounded-full bg-white p-1">
                      <img
                        src={user?.profileImage || "https://via.placeholder.com/80"}
                        alt="Your story"
                        className="w-full h-full rounded-full object-cover"
                      />
                    </div>
                  </div>
                  {/* Add More Story Button */}
                  <div 
                    className="absolute bottom-0 right-0 w-6 h-6 bg-pink-500 rounded-full flex items-center justify-center border-2 border-white cursor-pointer hover:bg-pink-600 transition-colors"
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowCreateStory(true);
                    }}
                    data-testid="add-more-story-btn"
                  >
                    <Plus className="w-4 h-4 text-white" />
                  </div>
                  <p className="text-xs mt-2 text-gray-700 font-medium">Your Story</p>
                </div>
              ) : (
                <div onClick={() => setShowCreateStory(true)}>
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-pink-200 to-rose-200 p-1 border-4 border-white shadow-lg hover:scale-105 transition-transform">
                    <div className="w-full h-full rounded-full bg-white p-0.5">
                      <img
                        src={user?.profileImage || "https://via.placeholder.com/80"}
                        alt="Add story"
                        className="w-full h-full rounded-full object-cover"
                      />
                    </div>
                  </div>
                  {/* Plus Button Overlay */}
                  <div className="absolute bottom-0 right-0 w-6 h-6 bg-pink-500 rounded-full flex items-center justify-center border-2 border-white cursor-pointer hover:bg-pink-600 transition-colors">
                    <Plus className="w-4 h-4 text-white" />
                  </div>
                  <p className="text-xs mt-2 text-gray-700 font-medium">Add Story</p>
                </div>
              )}
            </div>

            {/* Other Users' Stories */}
            {otherStories.map((storyGroup) => (
              <div 
                key={storyGroup.userId} 
                className="flex-shrink-0 text-center cursor-pointer"
                onClick={() => openStoryViewer(storyGroup)}
                data-testid={`story-circle-${storyGroup.userId}`}
              >
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
                <div className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <img
                      src={post.userProfileImage || "https://via.placeholder.com/40"}
                      alt={post.username}
                      className="w-10 h-10 rounded-full object-cover border-2 border-pink-200"
                    />
                    <div>
                      <p className="font-semibold text-gray-800">{post.username}</p>
                      <p className="text-xs text-gray-500">
                        {getRelativeTime(post.createdAt)}
                      </p>
                    </div>
                  </div>

                  {/* 3-Dot Menu - Only show for other users' posts */}
                  {post.userId !== user?.id && (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <button 
                          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                          data-testid={`post-menu-${post.id}`}
                        >
                          <MoreVertical className="w-5 h-5 text-gray-600" />
                        </button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent className="bg-white rounded-xl shadow-lg w-56" align="end">
                        <DropdownMenuItem 
                          onClick={() => handleSavePost(post.id)}
                          className="cursor-pointer hover:bg-pink-50 rounded-lg py-3"
                          data-testid={`save-post-menu-${post.id}`}
                        >
                          <Bookmark className={`w-4 h-4 mr-3 ${post.isSaved ? "fill-pink-500 text-pink-500" : ""}`} />
                          {post.isSaved ? "Unsave Post" : "Save Post"}
                        </DropdownMenuItem>
                        <DropdownMenuItem 
                          onClick={() => handleUnfollowFromPost(post.userId)}
                          className="cursor-pointer hover:bg-pink-50 rounded-lg py-3"
                          data-testid={`unfollow-menu-${post.id}`}
                        >
                          <UserIcon className="w-4 h-4 mr-3" />
                          Unfollow @{post.username}
                        </DropdownMenuItem>
                        <DropdownMenuItem 
                          onClick={() => {
                            setReportingPost(post);
                            setShowReportDialog(true);
                          }}
                          className="cursor-pointer hover:bg-red-50 text-red-600 rounded-lg py-3"
                          data-testid={`report-menu-${post.id}`}
                        >
                          <AlertCircle className="w-4 h-4 mr-3" />
                          Report Post
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}
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
                  <div className="flex justify-between items-center mb-3">
                    <div className="flex gap-4">
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
                    <button
                      onClick={() => handleSavePost(post.id)}
                      className="hover:scale-110 transition-transform"
                      data-testid={`save-btn-${post.id}`}
                    >
                      <Bookmark
                        className={`w-6 h-6 ${post.isSaved ? "fill-pink-500 text-pink-500" : "text-gray-700"}`}
                      />
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

      {/* Story Viewer Modal */}
      <Dialog open={showStoryViewer} onOpenChange={setShowStoryViewer}>
        <DialogContent className="bg-black max-w-md p-0 rounded-3xl overflow-hidden" data-testid="story-viewer">
          {viewingStories && viewingStories.stories[currentStoryIndex] && (
            <div className="relative w-full h-[600px]">
              {/* Close Button */}
              <button
                onClick={() => setShowStoryViewer(false)}
                className="absolute top-4 right-4 z-50 bg-black bg-opacity-50 rounded-full p-2 hover:bg-opacity-70 transition-opacity"
              >
                <X className="w-6 h-6 text-white" />
              </button>

              {/* 3-Dot Menu (Only for own stories) */}
              {viewingStories.userId === user?.id && (
                <div className="absolute top-4 right-16 z-50">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <button 
                        className="bg-black bg-opacity-50 rounded-full p-2 hover:bg-opacity-70 transition-opacity"
                        data-testid="story-menu-btn"
                      >
                        <MoreVertical className="w-6 h-6 text-white" />
                      </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="bg-white rounded-xl shadow-lg w-48" align="end">
                      <DropdownMenuItem 
                        onClick={() => openDeleteConfirm(viewingStories.stories[currentStoryIndex].id)}
                        className="cursor-pointer hover:bg-red-50 text-red-600 rounded-lg"
                        data-testid="delete-story-btn"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        onClick={handleSaveVideo}
                        className="cursor-pointer hover:bg-pink-50 rounded-lg"
                        data-testid="save-video-btn"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Save Video
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        onClick={handleCopyLink}
                        className="cursor-pointer hover:bg-pink-50 rounded-lg"
                        data-testid="copy-link-btn"
                      >
                        <Link2 className="w-4 h-4 mr-2" />
                        Copy Link
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        onClick={handleShareStory}
                        className="cursor-pointer hover:bg-pink-50 rounded-lg"
                        data-testid="share-story-btn"
                      >
                        <Share2 className="w-4 h-4 mr-2" />
                        Share
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              )}

              {/* Story Progress Bars */}
              <div className="absolute top-2 left-2 right-2 flex gap-1 z-40">
                {viewingStories.stories.map((_, index) => (
                  <div key={index} className="flex-1 h-1 bg-gray-400 bg-opacity-50 rounded-full overflow-hidden">
                    <div
                      className={`h-full bg-white transition-all duration-300 ${
                        index === currentStoryIndex ? "w-full" : index < currentStoryIndex ? "w-full" : "w-0"
                      }`}
                    />
                  </div>
                ))}
              </div>

              {/* User Info */}
              <div className="absolute top-6 left-4 flex items-center gap-2 z-40">
                <img
                  src={viewingStories.userProfileImage || "https://via.placeholder.com/40"}
                  alt={viewingStories.username}
                  className="w-8 h-8 rounded-full border-2 border-white"
                />
                <span className="text-white font-semibold text-sm">{viewingStories.username}</span>
              </div>

              {/* Story Content */}
              <div
                className="w-full h-full flex items-center justify-center bg-black cursor-pointer"
                onClick={nextStory}
              >
                {viewingStories.stories[currentStoryIndex].mediaType === "video" ? (
                  <video
                    src={viewingStories.stories[currentStoryIndex].mediaUrl}
                    autoPlay
                    className="max-w-full max-h-full object-contain"
                  />
                ) : (
                  <img
                    src={viewingStories.stories[currentStoryIndex].mediaUrl}
                    alt="Story"
                    className="max-w-full max-h-full object-contain"
                  />
                )}
              </div>

              {/* Caption */}
              {viewingStories.stories[currentStoryIndex].caption && (
                <div className="absolute bottom-4 left-4 right-4 bg-black bg-opacity-50 rounded-2xl p-3">
                  <p className="text-white text-sm">{viewingStories.stories[currentStoryIndex].caption}</p>
                </div>
              )}

              {/* Navigation Areas */}
              <div className="absolute inset-0 flex">
                <div
                  className="w-1/2 h-full cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    previousStory();
                  }}
                />
                <div className="w-1/2 h-full cursor-pointer" onClick={nextStory} />
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <DialogContent className="bg-white rounded-3xl" data-testid="delete-confirm-dialog">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-gray-800 text-center">
              Delete Story?
            </DialogTitle>
            <DialogDescription className="text-center text-gray-600 mt-4">
              Are you sure you want to delete this story? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="flex gap-3 mt-6">
            <Button
              onClick={() => {
                setShowDeleteConfirm(false);
                setStoryToDelete(null);
              }}
              variant="outline"
              className="flex-1 border-2 border-gray-300 hover:bg-gray-50 rounded-xl py-6"
              data-testid="cancel-delete-btn"
            >
              No, Keep It
            </Button>
            <Button
              onClick={handleDeleteStory}
              className="flex-1 bg-red-500 hover:bg-red-600 text-white rounded-xl py-6"
              data-testid="confirm-delete-btn"
            >
              Yes, Delete
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default HomePage;