import { useState, useEffect } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Crown, MoreVertical, Shield, AlertCircle, EyeOff, Link2, Share2, Zap, Lock } from "lucide-react";
import VerifiedBadge from "@/components/VerifiedBadge";
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

// Use a fallback so API calls don't break when the env var is missing
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

// Utility function to linkify bio text (mentions and URLs)
const LinkifyBio = ({ text }) => {
  if (!text) return null;
  
  const parts = text.split(/(@\w+|https?:\/\/[^\s]+)/g);
  
  return (
    <p className="text-gray-700 leading-relaxed">
      {parts.map((part, index) => {
        if (part.startsWith('@')) {
          // Make @mentions clickable
          return (
            <span key={index} className="text-blue-600 hover:underline cursor-pointer font-medium">
              {part}
            </span>
          );
        } else if (part.startsWith('http')) {
          // Make URLs clickable
          return (
            <a 
              key={index} 
              href={part} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              {part}
            </a>
          );
        }
        return <span key={index}>{part}</span>;
      })}
    </p>
  );
};

const ProfilePage = ({ user, onLogout }) => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [viewingUser, setViewingUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [userPosts, setUserPosts] = useState([]);
  const [showPremiumPopup, setShowPremiumPopup] = useState(false);
  const [showVibeCompatibility, setShowVibeCompatibility] = useState(false);
  const [vibeScore, setVibeScore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [followingInProgress, setFollowingInProgress] = useState(new Set());
  const [showVerificationPopover, setShowVerificationPopover] = useState(false);
  const [verificationDetails, setVerificationDetails] = useState(null);

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

  const fetchVerificationDetails = async (userId) => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API}/users/${userId}/verification-details`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setVerificationDetails(response.data);
      setShowVerificationPopover(true);
    } catch (error) {
      console.error("Error fetching verification details:", error);
    }
  };

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
      console.log(`Fetching vibe compatibility for user: ${viewingUser.id}`);
      
      const response = await axios.get(`${API}/auth/calculate-compatibility/${viewingUser.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log("Vibe compatibility response:", response.data);
      setVibeScore(response.data);
    } catch (error) {
      console.error("Error calculating vibe compatibility:", error);
      alert("Failed to calculate vibe compatibility. Please try again.");
      setShowVibeCompatibility(false);
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

  const handleFollowToggle = async (targetUserId, isFollowing, hasRequested) => {
    // Prevent multiple simultaneous follow actions on same user
    if (followingInProgress.has(targetUserId)) {
      return;
    }

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        console.error("No authentication token found");
        return;
      }

      // Add to following in progress
      setFollowingInProgress(prev => new Set(prev).add(targetUserId));

      let endpoint, newState;
      
      if (hasRequested) {
        // Cancel follow request
        endpoint = "cancel-follow-request";
        newState = { isFollowing: false, hasRequested: false };
      } else if (isFollowing) {
        // Unfollow
        endpoint = "unfollow";
        newState = { isFollowing: false, hasRequested: false };
      } else {
        // Follow or send request
        endpoint = "follow";
      }

      console.log(`Action: ${endpoint} for user ${targetUserId}`);
      
      const response = await axios.post(`${API}/users/${targetUserId}/${endpoint}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log("Follow action response:", response.data);
      
      // Update state based on response
      if (endpoint === "follow") {
        const wasRequestSent = response.data.requested === true;
        newState = wasRequestSent 
          ? { isFollowing: false, hasRequested: true }
          : { isFollowing: true, hasRequested: false };
      }
      
      if (viewingUser && viewingUser.id === targetUserId) {
        setViewingUser(prev => ({
          ...prev,
          ...newState,
          followersCount: newState.isFollowing && !isFollowing
            ? prev.followersCount + 1 
            : (!newState.isFollowing && isFollowing ? Math.max(0, prev.followersCount - 1) : prev.followersCount)
        }));
      }

      // Refresh profile data to get updated state
      await fetchUserProfile(targetUserId);
      await fetchUserPosts(targetUserId);
      
    } catch (error) {
      console.error("Error toggling follow:", error);
      if (error.response) {
        console.error("Response error:", error.response.data);
        alert(error.response.data.detail || "Failed to process request");
      } else {
        alert("Failed to process request. Please try again.");
      }
    } finally {
      // Remove from following in progress
      setFollowingInProgress(prev => {
        const newSet = new Set(prev);
        newSet.delete(targetUserId);
        return newSet;
      });
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
    // Redirect to MyProfile immediately if viewing own profile
    navigate("/my-profile", { replace: true });
    return null; // Don't render anything during redirect
  }

  if (isViewingSpecificUser) {
    // Individual User Profile View
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-pink-100" data-testid="user-profile-page">
        {/* Header */}
        <header className="glass-effect border-b border-pink-100">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <Button 
              variant="ghost" 
              className="hover:bg-pink-50"
              onClick={() => navigate(-1)}
            >
              <ArrowLeft className="w-5 h-5 text-pink-600" />
            </Button>
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
                src={
                  viewingUser?.profileImage 
                    ? (viewingUser.profileImage.startsWith('http') || viewingUser.profileImage.startsWith('data:')
                        ? viewingUser.profileImage 
                        : `${BACKEND_URL}${viewingUser.profileImage}`)
                    : "https://via.placeholder.com/120"
                }
                alt={viewingUser?.username}
                className="w-32 h-32 rounded-full object-cover mx-auto border-4 border-pink-200 shadow-lg mb-4"
                onError={(e) => {
                  e.target.src = "https://via.placeholder.com/120";
                }}
              />
              <h2 className="text-3xl font-bold text-gray-800 mb-1">{viewingUser?.fullName}</h2>
              <div className="flex items-center justify-center gap-1 mb-2">
                <p className="text-lg text-gray-600">@{viewingUser?.username}</p>
                {viewingUser?.isVerified && (
                  <button 
                    onClick={() => fetchVerificationDetails(viewingUser.id)}
                    className="hover:opacity-70 transition-opacity"
                    title="View verification details"
                  >
                    <VerifiedBadge size="md" />
                  </button>
                )}
                {viewingUser?.isFounder && (
                  <span className="text-2xl" title="Official LuvHive Account">👑</span>
                )}
              </div>
              
              {/* Official Account Badge */}
              {viewingUser?.isFounder && (
                <div className="inline-block bg-gradient-to-r from-purple-500 to-purple-600 text-white text-xs font-bold px-3 py-1 rounded-full mb-2 shadow-md">
                  🏢 Official LuvHive Account
                </div>
              )}
              
              {/* Verification Pathway Display */}
              {viewingUser?.isVerified && viewingUser?.verificationPathway && !viewingUser?.isFounder && (
                <p className="text-xs text-gray-500 mb-2">
                  Verified via: {viewingUser.verificationPathway}
                </p>
              )}
              
              {/* Private Account Badge */}
              {viewingUser?.isPrivate && (
                <div className="flex items-center justify-center gap-2 mb-3">
                  <Lock className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-600">Private Account</span>
                </div>
              )}
              
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
              <div className="flex gap-2 mt-6">
                <Button
                  onClick={() => handleFollowToggle(viewingUser?.id, viewingUser?.isFollowing, viewingUser?.hasRequested)}
                  data-testid="follow-user-btn"
                  variant={viewingUser?.isFollowing ? "outline" : (viewingUser?.hasRequested ? "outline" : "default")}
                  disabled={followingInProgress.has(viewingUser?.id)}
                  className={
                    viewingUser?.hasRequested
                      ? "flex-1 border-2 border-gray-400 text-gray-700 hover:bg-gray-50 rounded-xl py-3 text-sm"
                      : viewingUser?.isFollowing 
                        ? "flex-1 border-2 border-pink-500 text-pink-600 hover:bg-pink-50 rounded-xl py-3 text-sm" 
                        : "flex-1 bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white rounded-xl py-3 text-sm"
                  }
                >
                  {followingInProgress.has(viewingUser?.id) ? (
                    <div className="flex items-center justify-center gap-1">
                      <div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-xs">
                        {viewingUser?.hasRequested ? 'Canceling...' : (viewingUser?.isFollowing ? 'Unfollowing...' : 'Requesting...')}
                      </span>
                    </div>
                  ) : (
                    viewingUser?.hasRequested ? "Requested" : (viewingUser?.isFollowing ? "Following" : "Follow")
                  )}
                </Button>
                
                <Button
                  onClick={handleVibeCompatibility}
                  data-testid="vibe-compatibility-btn"
                  className="flex-1 bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white rounded-xl py-3 text-sm"
                >
                  <Zap className="w-4 h-4 mr-1" />
                  Vibe
                </Button>
                
                <Link to={`/chat/${viewingUser?.id}`} className="flex-1">
                  <Button
                    data-testid="premium-chat-user-btn"
                    variant="outline"
                    className="w-full border-2 border-purple-500 text-purple-600 hover:bg-purple-50 rounded-xl py-3 text-sm"
                  >
                    <Crown className="w-4 h-4 mr-1" />
                    Chat
                  </Button>
                </Link>
              </div>
            </div>
          </div>

          {/* User Posts Grid */}
          {viewingUser?.isPrivate && !viewingUser?.isFollowing ? (
            <div className="glass-effect rounded-3xl overflow-hidden shadow-xl">
              <div className="bg-gradient-to-br from-gray-100 to-gray-200 p-16 text-center">
                <div className="bg-white rounded-full w-32 h-32 mx-auto mb-6 flex items-center justify-center shadow-lg">
                  <Lock className="w-16 h-16 text-gray-400" />
                </div>
                <h3 className="text-3xl font-bold text-gray-800 mb-3">This Account is Private</h3>
                <p className="text-gray-600 text-lg mb-2">
                  Follow @{viewingUser?.username} to see their photos and videos
                </p>
                {viewingUser?.hasRequested && (
                  <div className="mt-4 inline-block bg-blue-50 text-blue-700 px-4 py-2 rounded-full text-sm font-medium">
                    ✓ Follow request sent
                  </div>
                )}
              </div>
            </div>
          ) : userPosts && userPosts.length > 0 ? (
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
          ) : null}
        </div>

        {/* Vibe Check Dialog */}
        <Dialog open={showVibeCompatibility} onOpenChange={setShowVibeCompatibility}>
          <DialogContent className="bg-white rounded-3xl max-w-md" data-testid="vibe-compatibility-dialog">
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-500">
                Vibe Check
              </DialogTitle>
            </DialogHeader>
            <div className="text-center py-4">
              {vibeScore !== null ? (
                <div className="space-y-3">
                  {/* Main Score */}
                  <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-500">
                    {vibeScore.compatibility_percentage}%
                  </div>
                  <p className="text-sm text-gray-600">
                    {vibeScore.message}
                  </p>
                  
                  {/* Breakdown in Grid - All 3 in one view */}
                  <div className="grid grid-cols-3 gap-2 mt-4">
                    {/* Total Score */}
                    <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl p-3">
                      <div className="text-2xl font-bold text-purple-600">
                        {vibeScore.compatibility_percentage}%
                      </div>
                      <div className="text-xs text-gray-600 mt-1">Overall</div>
                    </div>
                    
                    {/* Interest Match */}
                    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-3">
                      <div className="text-2xl font-bold text-blue-600">
                        {vibeScore.interest_score}%
                      </div>
                      <div className="text-xs text-gray-600 mt-1">Interests</div>
                    </div>
                    
                    {/* Personality Match */}
                    <div className="bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl p-3">
                      <div className="text-2xl font-bold text-pink-600">
                        {vibeScore.personality_score}%
                      </div>
                      <div className="text-xs text-gray-600 mt-1">Personality</div>
                    </div>
                  </div>
                  
                  {/* Common Interests */}
                  {vibeScore.common_interests && vibeScore.common_interests.length > 0 && (
                    <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-3 mt-3">
                      <div className="text-xs font-semibold text-gray-700 mb-2">❤️ Common Interests</div>
                      <div className="flex flex-wrap gap-1">
                        {vibeScore.common_interests.map((interest, idx) => (
                          <span key={idx} className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                            {interest}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-3 py-4">
                  <div className="animate-spin w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full mx-auto"></div>
                  <p className="text-sm text-gray-600">
                    Calculating vibe...
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
                      disabled={followingInProgress.has(u.id)}
                      className={u.isFollowing ? "border-pink-500 text-pink-600 hover:bg-pink-50 rounded-full min-w-[80px]" : "bg-pink-500 hover:bg-pink-600 text-white rounded-full min-w-[80px]"}
                    >
                      {followingInProgress.has(u.id) ? (
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin"></div>
                          <span className="text-xs">{u.isFollowing ? 'Unfollowing...' : 'Following...'}</span>
                        </div>
                      ) : (
                        u.isFollowing ? "Following" : "Follow"
                      )}
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

      {/* Verification Details Popover */}
      <Dialog open={showVerificationPopover} onOpenChange={setShowVerificationPopover}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-blue-500" />
              {verificationDetails?.pathway === "Official LuvHive Account" ? "Official Account" : "Verification Details"}
            </DialogTitle>
          </DialogHeader>
          
          {verificationDetails && (
            <div className="space-y-4 py-4">
              {verificationDetails.pathway === "Official LuvHive Account" ? (
                // Special display for Official LuvHive Account
                <>
                  <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg border border-purple-200">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">👑</span>
                      <p className="font-bold text-gray-800">Official LuvHive Account</p>
                    </div>
                    <p className="text-sm text-gray-700 mb-1">
                      <span className="font-semibold">Founder & Admin</span>
                    </p>
                    <p className="text-xs text-gray-600">
                      Verified on {new Date(verificationDetails.verifiedAt).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
                    </p>
                  </div>
                  
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-sm text-red-800 font-medium mb-1">⚠️ Impersonation Guard</p>
                    <p className="text-xs text-red-700">
                      If you see duplicate accounts claiming to be LuvHive, please report them via @LuvHiveSupport or through the report feature.
                    </p>
                  </div>
                </>
              ) : (
                // Regular verification display
                <>
                  <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-4 rounded-lg border border-blue-200">
                    <p className="text-sm text-gray-700 mb-2">
                      <span className="font-semibold">Verified via:</span> {verificationDetails.pathway}
                    </p>
                    <p className="text-xs text-gray-600">
                      <span className="font-semibold">Verified on:</span> {new Date(verificationDetails.verifiedAt).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
                    </p>
                  </div>
                  
                  <div className="text-sm text-gray-600 leading-relaxed">
                    <p className="font-semibold mb-2">About this pathway:</p>
                    {verificationDetails.pathway === 'High Engagement Pathway' && (
                      <p>This user achieved verification through exceptional community engagement with 20+ posts, 100+ followers, and significant likes and views.</p>
                    )}
                    {verificationDetails.pathway === 'Moderate Engagement Pathway' && (
                      <p>This user achieved verification through consistent activity over 90+ days with 10+ posts, 50+ followers, and strong engagement metrics.</p>
                    )}
                    {verificationDetails.pathway === 'Community Contribution' && (
                      <p>This user achieved verification through valuable community contributions such as moderation, event organization, or helpful reporting.</p>
                    )}
                    {verificationDetails.pathway === 'Cross-Platform Verified' && (
                      <p>This user achieved verification by linking their verified account from another major social media platform.</p>
                    )}
                  </div>
                </>
              )}
              
              <Button 
                onClick={() => setShowVerificationPopover(false)}
                className="w-full bg-blue-500 hover:bg-blue-600 text-white"
              >
                Got it!
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ProfilePage;