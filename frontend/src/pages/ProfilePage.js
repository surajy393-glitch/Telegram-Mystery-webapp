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
    fetchProfile();
    fetchUsers();
  }, []);

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

  const handleFollowToggle = async (userId, isFollowing) => {
    try {
      const token = localStorage.getItem("token");
      const endpoint = isFollowing ? "unfollow" : "follow";
      await axios.post(`${API}/users/${userId}/${endpoint}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchUsers(); // Refresh users list
      fetchProfile(); // Update followers count
    } catch (error) {
      console.error("Error toggling follow:", error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-pink-50 to-white">
        <div className="text-2xl text-pink-600">Loading...</div>
      </div>
    );
  }

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
            Profile
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
                  <img
                    src={u.profileImage || "https://via.placeholder.com/48"}
                    alt={u.username}
                    className="w-12 h-12 rounded-full object-cover border-2 border-pink-200"
                  />
                  <div className="flex-1">
                    <p className="font-semibold text-gray-800">{u.fullName}</p>
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