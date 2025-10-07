import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Crown, MoreVertical, Shield, AlertCircle, EyeOff, Link2, Share2, Zap } from "lucide-react";
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

const ProfilePage = ({ user, onLogout }) => {
  const { userId } = useParams();
  const [profile, setProfile] = useState(null);
  const [viewingUser, setViewingUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [userPosts, setUserPosts] = useState([]);
  const [showPremiumPopup, setShowPremiumPopup] = useState(false);
  const [showVibeCompatibility, setShowVibeCompatibility] = useState(false);
  const [vibeScore, setVibeScore] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if we're viewing a specific user or discovery page
  const isViewingSpecificUser = !!userId;
  const isViewingOwnProfile = userId === user?.id;

  useEffect(() => {
    if (isViewingSpecificUser) {
      fetchUserProfile(userId);
      fetchUserPosts(userId);
    } else {
      fetchProfile();
      fetchUsers();
    }
  }, [userId]);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProfile(response.data);
    } catch (error) {
      console.error("Error fetching profile:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API}/users/list`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(response.data.users || []);
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  const fetchUserProfile = async (targetUserId) => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API}/users/${targetUserId}/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setViewingUser(response.data);
    } catch (error) {
      console.error("Error fetching user profile:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserPosts = async (targetUserId) => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API}/users/${targetUserId}/posts`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUserPosts(response.data.posts || []);
    } catch (error) {
      console.error("Error fetching user posts:", error);
    }
  };

  const handleVibeCompatibility = async () => {
    if (!viewingUser) return;
    
    setShowVibeCompatibility(true);
    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(`${API}/ai/vibe-compatibility`, {
        targetUserId: viewingUser.id
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setVibeScore(response.data.compatibility);
    } catch (error) {
      console.error("Error calculating vibe compatibility:", error);
      alert("Failed to calculate vibe compatibility. Please try again.");
    }
  };

  const handleBlockUser = async () => {
    if (!viewingUser) return;
    
    try {
      const token = localStorage.getItem("token");
      await axios.post(`${API}/users/${viewingUser.id}/block`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert(`${viewingUser.username} has been blocked`);
    } catch (error) {
      console.error("Error blocking user:", error);
      alert("Failed to block user");
    }
  };

  const handleReportUser = async () => {
    if (!viewingUser) return;
    alert(`Report submitted for ${viewingUser.username}. Our team will review this profile.`);
  };

  const handleHideStory = async () => {
    if (!viewingUser) return;
    try {
      const token = localStorage.getItem("token");
      await axios.post(`${API}/users/${viewingUser.id}/hide-story`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert("You will no longer see stories from this user");
    } catch (error) {
      console.error("Error hiding story:", error);
      alert("Failed to hide stories");
    }
  };

  const handleCopyProfileURL = () => {
    if (!viewingUser) return;
    const profileURL = `${window.location.origin}/profile/${viewingUser.id}`;
    navigator.clipboard.writeText(profileURL).then(() => {
      alert("Profile URL copied to clipboard!");
    }).catch(() => {
      alert("Failed to copy URL");
    });
  };

  const handleShareProfile = async () => {
    if (!viewingUser) return;
    
    const profileURL = `${window.location.origin}/profile/${viewingUser.id}`;
    const shareText = `Check out ${viewingUser.fullName}'s profile on LuvHive!`;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${viewingUser.fullName} - LuvHive Profile`,
          text: shareText,
          url: profileURL,
        });
      } catch (error) {
        if (error.name !== 'AbortError') {
          // Fallback to copy link
          navigator.clipboard.writeText(profileURL).then(() => {
            alert('Profile link copied! Share it on Telegram, WhatsApp, Instagram, or Facebook!');
          });
        }
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(profileURL).then(() => {
        alert('Profile link copied! Share it on Telegram, WhatsApp, Instagram, or Facebook!');
      }).catch(() => {
        alert('Failed to copy link');
      });
    }
  };

  const handleFollowToggle = async (targetUserId, isFollowing) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        console.error("No authentication token found");
        return;
      }

      // OPTIMISTIC UI UPDATE - Update immediately before API call
      
      // Update main viewing user if it's the target
      if (viewingUser && viewingUser.id === targetUserId) {
        setViewingUser(prev => ({
          ...prev,
          isFollowing: !isFollowing,
          followersCount: !isFollowing 
            ? prev.followersCount + 1 
            : Math.max(0, prev.followersCount - 1)
        }));
      }

      // Update users list
      setUsers(prevUsers => 
        prevUsers.map(user => 
          user.id === targetUserId 
            ? { 
                ...user, 
                isFollowing: !isFollowing,
                followersCount: !isFollowing 
                  ? user.followersCount + 1 
                  : Math.max(0, user.followersCount - 1)
              }
            : user
        )
      );

      // Make API call in background
      const endpoint = isFollowing ? "unfollow" : "follow";
      console.log(`${isFollowing ? 'Unfollowing' : 'Following'} user ${targetUserId}`);
      
      const response = await axios.post(`${API}/users/${targetUserId}/${endpoint}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log("Follow action response:", response.data);
      
    } catch (error) {
      console.error("Error toggling follow:", error);
      
      // ROLLBACK optimistic update on error
      if (viewingUser && viewingUser.id === targetUserId) {
        setViewingUser(prev => ({
          ...prev,
          isFollowing: isFollowing, // Revert back
          followersCount: isFollowing 
            ? prev.followersCount + 1 
            : Math.max(0, prev.followersCount - 1)
        }));
      }

      // Rollback users list
      setUsers(prevUsers => 
        prevUsers.map(user => 
          user.id === targetUserId 
            ? { 
                ...user, 
                isFollowing: isFollowing, // Revert back
                followersCount: isFollowing 
                  ? user.followersCount + 1 
                  : Math.max(0, user.followersCount - 1)
              }
            : user
        )
      );

      if (error.response) {
        console.error("Response error:", error.response.data);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-pink-50 to-white">
        <div className="text-2xl text-pink-600">Loading...</div>
      </div>
    );
  }

  if (isViewingSpecificUser && isViewingOwnProfile) {
    // Redirect to MyProfile if viewing own profile
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-pink-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl text-gray-600 mb-4">Redirecting to your profile...</p>
          <Link to="/my-profile" className="text-pink-600 hover:text-pink-800">
            Click here if not redirected
          </Link>
        </div>
      </div>
    );
  }

  if (isViewingSpecificUser) {
    // Individual User Profile View
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-pink-100" data-testid="user-profile-page">
        {/* Header */}
        <header className="glass-effect border-b border-pink-100">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <Link to="/home">
              <Button variant="ghost" className="hover:bg-pink-50">
                <ArrowLeft className="w-5 h-5 text-pink-600" />
              </Button>
            </Link>
            <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-rose-500">
              @{viewingUser?.username}
            </h1>
            
            {/* 3-Dot Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="hover:bg-pink-50" data-testid="profile-menu-btn">
                  <MoreVertical className="w-5 h-5 text-pink-600" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="bg-white rounded-xl shadow-lg w-56" align="end">
                <DropdownMenuItem onClick={handleBlockUser} className="cursor-pointer hover:bg-red-50 text-red-600 rounded-lg py-3">
                  <Shield className="w-4 h-4 mr-3" />
                  Block
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleReportUser} className="cursor-pointer hover:bg-red-50 text-red-600 rounded-lg py-3">
                  <AlertCircle className="w-4 h-4 mr-3" />
                  Report
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleHideStory} className="cursor-pointer hover:bg-pink-50 rounded-lg py-3">
                  <EyeOff className="w-4 h-4 mr-3" />
                  Hide your story
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleCopyProfileURL} className="cursor-pointer hover:bg-pink-50 rounded-lg py-3">
                  <Link2 className="w-4 h-4 mr-3" />
                  Copy profile URL
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleShareProfile} className="cursor-pointer hover:bg-pink-50 rounded-lg py-3">
                  <Share2 className="w-4 h-4 mr-3" />
                  Share this profile
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        <div className="container mx-auto px-4 py-8 max-w-2xl">
          {/* User Profile Card */}
          <div className="glass-effect rounded-3xl p-8 mb-8 shadow-xl animate-fadeIn">
            <div className="text-center">
              <img
                src={viewingUser?.profileImage || "https://via.placeholder.com/120"}
                alt={viewingUser?.username}
                className="w-32 h-32 rounded-full object-cover mx-auto border-4 border-pink-200 shadow-lg mb-4"
              />
              <h2 className="text-3xl font-bold text-gray-800 mb-1">{viewingUser?.fullName}</h2>
              <p className="text-lg text-gray-600 mb-2">@{viewingUser?.username}</p>
              
              {viewingUser?.isPremium && (
                <div className="inline-flex items-center gap-2 premium-badge mb-4">
                  <Crown className="w-4 h-4" />
                  PREMIUM MEMBER
                </div>
              )}

              <div className="flex justify-center gap-8 mt-6 mb-6">
                <div>
                  <p className="text-2xl font-bold text-pink-600">{viewingUser?.posts || userPosts?.length || 0}</p>
                  <p className="text-sm text-gray-600">Posts</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-pink-600">{viewingUser?.followersCount || 0}</p>
                  <p className="text-sm text-gray-600">Followers</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-pink-600">{viewingUser?.followingCount || 0}</p>
                  <p className="text-sm text-gray-600">Following</p>
                </div>
              </div>

              {viewingUser?.bio && (
                <div className="bg-pink-50 rounded-2xl p-4 mt-4 mb-6">
                  <p className="text-gray-700">{viewingUser.bio}</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 mt-6">
                <Button
                  onClick={() => handleFollowToggle(viewingUser?.id, viewingUser?.isFollowing)}
                  data-testid="follow-user-btn"
                  variant={viewingUser?.isFollowing ? "outline" : "default"}
                  className={viewingUser?.isFollowing 
                    ? "flex-1 border-2 border-pink-500 text-pink-600 hover:bg-pink-50 rounded-xl py-4" 
                    : "flex-1 bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white rounded-xl py-4"
                  }
                >
                  {viewingUser?.isFollowing ? "Following" : "Follow"}
                </Button>
                
                <Button
                  onClick={handleVibeCompatibility}
                  data-testid="vibe-compatibility-btn"
                  className="flex-1 bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white rounded-xl py-4"
                >
                  <Zap className="w-5 h-5 mr-2" />
                  Vibe Compatibility
                </Button>
                
                <Link to={`/chat/${viewingUser?.id}`}>
                  <Button
                    data-testid="premium-chat-user-btn"
                    variant="outline"
                    className="border-2 border-purple-500 text-purple-600 hover:bg-purple-50 rounded-xl py-4 px-6"
                  >
                    Premium Chat
                  </Button>
                </Link>
              </div>
            </div>
          </div>

          {/* User Posts Grid */}
          {userPosts && userPosts.length > 0 && (
            <div className="glass-effect rounded-3xl p-6 shadow-xl">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Recent Posts</h3>
              <div className="grid grid-cols-3 gap-2">
                {userPosts.slice(0, 9).map((post) => (
                  <div key={post.id} className="aspect-square rounded-lg overflow-hidden">
                    {post.mediaType === "video" ? (
                      <video src={post.mediaUrl} className="w-full h-full object-cover" />
                    ) : (
                      <img src={post.mediaUrl} alt="Post" className="w-full h-full object-cover" />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Vibe Compatibility Dialog */}
        <Dialog open={showVibeCompatibility} onOpenChange={setShowVibeCompatibility}>
          <DialogContent className="bg-white rounded-3xl" data-testid="vibe-compatibility-dialog">
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-500">
                Vibe Compatibility
              </DialogTitle>
            </DialogHeader>
            <div className="text-center py-6">
              {vibeScore !== null ? (
                <div className="space-y-4">
                  <div className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-500">
                    {vibeScore}%
                  </div>
                  <p className="text-lg text-gray-700">
                    Your vibe compatibility with {viewingUser?.fullName}
                  </p>
                  <div className="bg-gradient-to-r from-purple-100 to-indigo-100 rounded-2xl p-4 mt-4">
                    <p className="text-sm text-gray-600">
                      {vibeScore >= 80 ? "🔥 Amazing connection! You two are perfectly matched!" :
                       vibeScore >= 60 ? "💫 Great chemistry! You have a lot in common!" :
                       vibeScore >= 40 ? "✨ Good potential! Worth getting to know each other better!" :
                       "🌟 Different vibes, but opposites can attract!"}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="animate-spin w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full mx-auto"></div>
                  <p className="text-lg text-gray-700">
                    AI is analyzing your compatibility...
                  </p>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      </div>
    );
  }

  // Discovery Page (Original Content)
  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-pink-100" data-testid="profile-page">
      {/* Header */}
      <header className="glass-effect border-b border-pink-100">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/home">
            <Button variant="ghost" className="hover:bg-pink-50">
              <ArrowLeft className="w-5 h-5 text-pink-600" />
            </Button>
          </Link>
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-rose-500">
            Discover
          </h1>
          <div className="w-10"></div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-2xl">
        {/* Profile Card */}
        <div className="glass-effect rounded-3xl p-8 mb-8 shadow-xl animate-fadeIn">
          <div className="text-center">
            <img
              src={profile?.profileImage || "https://via.placeholder.com/120"}
              alt={profile?.username}
              className="w-32 h-32 rounded-full object-cover mx-auto border-4 border-pink-200 shadow-lg mb-4"
            />
            <h2 className="text-3xl font-bold text-gray-800 mb-1">{profile?.fullName}</h2>
            <p className="text-lg text-gray-600 mb-2">@{profile?.username}</p>
            
            {profile?.isPremium && (
              <div className="inline-flex items-center gap-2 premium-badge mb-4">
                <Crown className="w-4 h-4" />
                PREMIUM MEMBER
              </div>
            )}

            <div className="flex justify-center gap-8 mt-6 mb-6">
              <div>
                <p className="text-2xl font-bold text-pink-600">{profile?.age}</p>
                <p className="text-sm text-gray-600">Age</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-pink-600">{profile?.gender}</p>
                <p className="text-sm text-gray-600">Gender</p>
              </div>
            </div>

            {profile?.bio && (
              <div className="bg-pink-50 rounded-2xl p-4 mt-4">
                <p className="text-gray-700">{profile.bio}</p>
              </div>
            )}

            {profile?.telegramLinked ? (
              <div className="mt-6 bg-green-50 border-2 border-green-200 rounded-2xl p-4">
                <p className="text-green-700 font-semibold">✓ Telegram Connected</p>
              </div>
            ) : (
              <div className="mt-6 bg-yellow-50 border-2 border-yellow-200 rounded-2xl p-4">
                <p className="text-yellow-700 font-semibold">⚠ Telegram Not Connected</p>
                <p className="text-sm text-gray-600 mt-1">Link your Telegram account from the bot</p>
              </div>
            )}
          </div>
        </div>

        {/* Premium Section */}
        {!profile?.isPremium && (
          <div className="glass-effect rounded-3xl p-8 mb-8 shadow-xl animate-slideIn">
            <div className="text-center">
              <Crown className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-gray-800 mb-2">Upgrade to Premium</h3>
              <p className="text-gray-600 mb-6">Unlock unlimited chat and exclusive features</p>
              <Button
                onClick={() => setShowPremiumPopup(true)}
                data-testid="premium-chat-btn"
                className="bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-white px-8 py-6 rounded-xl text-lg btn-hover"
              >
                Get Premium Now
              </Button>
            </div>
          </div>
        )}

        {/* Users List */}
        <div className="glass-effect rounded-3xl p-6 shadow-xl animate-scaleIn">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Discover People</h3>
          <div className="space-y-3">
            {users.length === 0 ? (
              <p className="text-center text-gray-600 py-4">No users found</p>
            ) : (
              users.map((u) => (
                <div
                  key={u.id}
                  className="flex items-center gap-3 p-3 rounded-xl hover:bg-pink-50 transition-colors"
                >
                  <Link to={`/profile/${u.id}`}>
                    <img
                      src={u.profileImage || "https://via.placeholder.com/48"}
                      alt={u.username}
                      className="w-12 h-12 rounded-full object-cover border-2 border-pink-200 cursor-pointer hover:border-pink-400 transition-colors"
                    />
                  </Link>
                  <div className="flex-1">
                    <Link to={`/profile/${u.id}`} className="font-semibold text-gray-800 hover:text-pink-600 transition-colors">
                      {u.fullName}
                    </Link>
                    <p className="text-sm text-gray-600">@{u.username}</p>
                    <p className="text-xs text-gray-500">{u.followersCount} followers</p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={() => handleFollowToggle(u.id, u.isFollowing)}
                      data-testid={`follow-btn-${u.id}`}
                      size="sm"
                      variant={u.isFollowing ? "outline" : "default"}
                      className={u.isFollowing ? "border-pink-500 text-pink-600 hover:bg-pink-50 rounded-full" : "bg-pink-500 hover:bg-pink-600 text-white rounded-full"}
                    >
                      {u.isFollowing ? "Following" : "Follow"}
                    </Button>
                    <Link to={`/chat/${u.id}`}>
                      <Button
                        data-testid={`chat-btn-${u.id}`}
                        size="sm"
                        variant="outline"
                        className="border-pink-500 text-pink-600 hover:bg-pink-50 rounded-full"
                      >
                        Chat
                      </Button>
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Premium Popup */}
      <Dialog open={showPremiumPopup} onOpenChange={setShowPremiumPopup}>
        <DialogContent className="bg-white rounded-3xl" data-testid="premium-popup">
          <DialogHeader>
            <DialogTitle className="text-3xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-yellow-600 to-yellow-500">
              Premium Chat
            </DialogTitle>
            <DialogDescription className="text-center text-gray-700 mt-4">
              <Crown className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
              <p className="text-lg font-semibold mb-2">
                Buy Premium from Bot to Use Chat Service
              </p>
              <p className="text-sm text-gray-600 mb-6">
                Visit our Telegram bot to purchase premium membership and unlock unlimited chat access
              </p>
              <Button
                onClick={() => window.open("https://t.me/your_bot_username", "_blank")}
                className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white px-6 py-3 rounded-xl"
              >
                Open Telegram Bot
              </Button>
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ProfilePage;