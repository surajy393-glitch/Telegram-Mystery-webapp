import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Shield, ShieldCheck, Eye, EyeOff, Search, MessageCircle, Wifi, Tag, MessageSquare, Zap, Bell, BellOff, Mail, MailX, Download, HelpCircle, LogOut, X, UserMinus } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SettingsPage = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [settings, setSettings] = useState({
    // Mystery Match Privacy
    allowMatching: true,
    showInMatchPool: true,
    allowGenderRevealRequests: true,
    allowAgeRevealRequests: true,
    allowPhotoRevealRequests: true,
    
    // Notifications
    newMatchNotifications: true,
    newMessageNotifications: true,
    revealRequestNotifications: true,
    matchExpiryNotifications: true,
    emailNotifications: true,
    
    // Matching Preferences
    autoAcceptMatches: false,
    receivePremiumMatches: true
  });
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState({});
  const [showBlockedUsers, setShowBlockedUsers] = useState(false);
  const [blockedUsers, setBlockedUsers] = useState([]);

  useEffect(() => {
    fetchProfile();
  }, []);

  useEffect(() => {
    if (showBlockedUsers) {
      fetchBlockedUsers();
    }
  }, [showBlockedUsers]);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProfile(response.data);
      
      // Load all settings from profile
      setSettings({
        isPrivate: response.data.isPrivate || false,
        appearInSearch: response.data.appearInSearch !== false,
        allowDirectMessages: response.data.allowDirectMessages !== false,
        showOnlineStatus: response.data.showOnlineStatus !== false,
        allowTagging: response.data.allowTagging !== false,
        allowStoryReplies: response.data.allowStoryReplies !== false,
        showVibeScore: response.data.showVibeScore !== false,
        pushNotifications: response.data.pushNotifications !== false,
        emailNotifications: response.data.emailNotifications !== false
      });
      
      // Fetch blocked users if dialog is opened
      if (showBlockedUsers) {
        fetchBlockedUsers();
      }
    } catch (error) {
      console.error("Error fetching profile:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSettingToggle = async (settingKey) => {
    if (updating[settingKey]) return;
    
    setUpdating(prev => ({ ...prev, [settingKey]: true }));
    try {
      const token = localStorage.getItem("token");
      const newValue = !settings[settingKey];
      
      await axios.put(`${API}/auth/settings`, {
        [settingKey]: newValue
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSettings(prev => ({ ...prev, [settingKey]: newValue }));
    } catch (error) {
      console.error(`Error updating ${settingKey}:`, error);
      alert(`Failed to update ${settingKey.replace(/([A-Z])/g, ' $1').toLowerCase()}`);
    } finally {
      setUpdating(prev => ({ ...prev, [settingKey]: false }));
    }
  };

  const handleDownloadData = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API}/auth/download-data`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `luvhive-data-${profile?.username}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading data:", error);
      alert("Failed to download your data");
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate('/');
  };

  const fetchBlockedUsers = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API}/users/blocked`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setBlockedUsers(response.data.blockedUsers || []);
    } catch (error) {
      console.error("Error fetching blocked users:", error);
    }
  };

  const handleUnblockUser = async (userId) => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(`${API}/users/${userId}/unblock`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Remove from blocked users list
      setBlockedUsers(prev => prev.filter(user => user.id !== userId));
      
      // Update profile data
      setProfile(prev => ({
        ...prev,
        blockedUsers: (prev?.blockedUsers || []).filter(id => id !== userId)
      }));
      
      alert("User unblocked successfully");
    } catch (error) {
      console.error("Error unblocking user:", error);
      alert("Failed to unblock user");
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
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-pink-100" data-testid="settings-page">
      {/* Header */}
      <header className="glass-effect border-b border-pink-100 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/my-profile">
            <Button variant="ghost" className="hover:bg-pink-50">
              <ArrowLeft className="w-5 h-5 text-pink-600" />
            </Button>
          </Link>
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-rose-500">
            Settings
          </h1>
          <div className="w-10"></div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-2xl">
        {/* Profile Header */}
        <div className="glass-effect rounded-3xl p-6 mb-6 shadow-xl animate-fadeIn">
          <div className="flex items-center gap-4">
            <img
              src={profile?.profileImage || "https://via.placeholder.com/80"}
              alt={profile?.username}
              className="w-16 h-16 rounded-full object-cover border-4 border-pink-200 shadow-lg"
            />
            <div>
              <h2 className="text-xl font-bold text-gray-800">{profile?.fullName}</h2>
              <p className="text-gray-600">@{profile?.username}</p>
            </div>
          </div>
        </div>

        {/* Mystery Match Privacy Section */}
        <div className="glass-effect rounded-3xl p-6 mb-6 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 rounded-full bg-purple-100">
              <Shield className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800">🎭 Mystery Match Privacy</h3>
          </div>
          
          <div className="space-y-4">
            <SettingToggle
              icon={<Search className="w-5 h-5" />}
              label="Allow Matching"
              description="Enable others to match with you"
              isOn={settings.allowMatching}
              onToggle={() => handleSettingToggle('allowMatching')}
              loading={updating.allowMatching}
            />
            
            <SettingToggle
              icon={<Eye className="w-5 h-5" />}
              label="Show in Match Pool"
              description="Appear in the matching algorithm"
              isOn={settings.showInMatchPool}
              onToggle={() => handleSettingToggle('showInMatchPool')}
              loading={updating.showInMatchPool}
            />
            
            <SettingToggle
              icon={<Shield className="w-5 h-5" />}
              label="Allow Gender Reveal Requests"
              description="Others can request to see your gender at 30 messages"
              isOn={settings.allowGenderRevealRequests}
              onToggle={() => handleSettingToggle('allowGenderRevealRequests')}
              loading={updating.allowGenderRevealRequests}
            />
            
            <SettingToggle
              icon={<Shield className="w-5 h-5" />}
              label="Allow Age Reveal Requests"
              description="Others can request to see your age at 60 messages"
              isOn={settings.allowAgeRevealRequests}
              onToggle={() => handleSettingToggle('allowAgeRevealRequests')}
              loading={updating.allowAgeRevealRequests}
            />
            
            <SettingToggle
              icon={<Shield className="w-5 h-5" />}
              label="Allow Photo Reveal Requests"
              description="Others can request your photo at 120 messages"
              isOn={settings.allowPhotoRevealRequests}
              onToggle={() => handleSettingToggle('allowPhotoRevealRequests')}
              loading={updating.allowPhotoRevealRequests}
            />
          </div>
        </div>

        {/* Blocked Users Section */}
        <div className="glass-effect rounded-3xl p-6 mb-6 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 rounded-full bg-red-100">
              <UserMinus className="w-6 h-6 text-red-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800">Blocked Matches</h3>
          </div>
          
          <ActionButton
            icon={<UserMinus className="w-5 h-5" />}
            label="Manage Blocked Matches"
            description={`View and unblock matches (${profile?.blockedUsers?.length || 0} blocked)`}
            onClick={() => setShowBlockedUsers(true)}
            bgColor="bg-red-50 hover:bg-red-100"
            textColor="text-red-600"
          />
        </div>

        {/* Matching Preferences Section */}
        <div className="glass-effect rounded-3xl p-6 mb-6 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 rounded-full bg-pink-100">
              <Zap className="w-6 h-6 text-pink-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800">Matching Preferences</h3>
          </div>
          
          <div className="space-y-4">
            <SettingToggle
              icon={<Zap className="w-5 h-5" />}
              label="Auto-Accept Matches"
              description="Automatically accept all incoming match requests"
              isOn={settings.autoAcceptMatches}
              onToggle={() => handleSettingToggle('autoAcceptMatches')}
              loading={updating.autoAcceptMatches}
            />
            
            <SettingToggle
              icon={<Shield className="w-5 h-5" />}
              label="Receive Premium Matches"
              description="Get matched with premium users"
              isOn={settings.receivePremiumMatches}
              onToggle={() => handleSettingToggle('receivePremiumMatches')}
              loading={updating.receivePremiumMatches}
            />
          </div>
        </div>

        {/* Notifications Section */}
        <div className="glass-effect rounded-3xl p-6 mb-6 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 rounded-full bg-purple-100">
              <Bell className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800">Notifications</h3>
          </div>
          
          <div className="space-y-4">
            <SettingToggle
              icon={settings.pushNotifications ? <Bell className="w-5 h-5" /> : <BellOff className="w-5 h-5" />}
              label="Push Notifications"
              description="Receive notifications for sparks, glows, and messages"
              isOn={settings.pushNotifications}
              onToggle={() => handleSettingToggle('pushNotifications')}
              loading={updating.pushNotifications}
            />
            
            <SettingToggle
              icon={settings.emailNotifications ? <Mail className="w-5 h-5" /> : <MailX className="w-5 h-5" />}
              label="Email Notifications"
              description="Get email updates about your LuvHive activity"
              isOn={settings.emailNotifications}
              onToggle={() => handleSettingToggle('emailNotifications')}
              loading={updating.emailNotifications}
            />
          </div>
        </div>

        {/* Account Actions Section */}
        <div className="glass-effect rounded-3xl p-6 mb-6 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 rounded-full bg-red-100">
              <LogOut className="w-6 h-6 text-red-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800">Account Actions</h3>
          </div>
          
          <div className="space-y-4">
            <ActionButton
              icon={<Download className="w-5 h-5" />}
              label="Download Data"
              description="Export your LuvHive data"
              onClick={handleDownloadData}
              bgColor="bg-blue-50 hover:bg-blue-100"
              textColor="text-blue-600"
            />
            
            <ActionButton
              icon={<HelpCircle className="w-5 h-5" />}
              label="Help & Support"
              description="Get help with LuvHive"
              onClick={() => window.open('mailto:support@luvhive.com', '_blank')}
              bgColor="bg-green-50 hover:bg-green-100"
              textColor="text-green-600"
            />
            
            <ActionButton
              icon={<LogOut className="w-5 h-5" />}
              label="Logout"
              description="Sign out of LuvHive"
              onClick={handleLogout}
              bgColor="bg-red-50 hover:bg-red-100"
              textColor="text-red-600"
            />
          </div>
        </div>
      </div>

      {/* Blocked Users Dialog */}
      <Dialog open={showBlockedUsers} onOpenChange={setShowBlockedUsers}>
        <DialogContent className="bg-white rounded-3xl max-w-md" data-testid="blocked-users-dialog">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-gray-800 flex items-center gap-3">
              <Shield className="w-6 h-6 text-red-600" />
              Blocked Users
            </DialogTitle>
          </DialogHeader>
          
          <div className="mt-4">
            {blockedUsers.length === 0 ? (
              <div className="text-center py-8">
                <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No blocked users</p>
                <p className="text-sm text-gray-500 mt-2">
                  Users you block will appear here
                </p>
              </div>
            ) : (
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {blockedUsers.map((blockedUser) => (
                  <div key={blockedUser.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                    <div className="flex items-center gap-3">
                      <img
                        src={blockedUser.profileImage || "https://via.placeholder.com/40"}
                        alt={blockedUser.username}
                        className="w-10 h-10 rounded-full object-cover border-2 border-gray-300"
                      />
                      <div>
                        <p className="font-semibold text-gray-800">{blockedUser.fullName}</p>
                        <p className="text-sm text-gray-600">@{blockedUser.username}</p>
                      </div>
                    </div>
                    <Button
                      onClick={() => handleUnblockUser(blockedUser.id)}
                      size="sm"
                      variant="outline"
                      className="border-red-300 text-red-600 hover:bg-red-50 rounded-lg"
                    >
                      <UserMinus className="w-4 h-4 mr-2" />
                      Unblock
                    </Button>
                  </div>
                ))}
              </div>
            )}
            
            <div className="mt-6">
              <Button
                onClick={() => setShowBlockedUsers(false)}
                className="w-full bg-gray-500 hover:bg-gray-600 text-white rounded-xl py-3"
              >
                Close
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Helper Components
const SettingToggle = ({ icon, label, description, isOn, onToggle, loading }) => (
  <div 
    className="flex items-center justify-between p-4 bg-white rounded-2xl border-2 border-pink-100 hover:border-pink-200 transition-colors cursor-pointer"
    onClick={onToggle}
  >
    <div className="flex items-center gap-4">
      {icon && (
        <div className={`p-2 rounded-full ${isOn ? 'bg-pink-100 text-pink-600' : 'bg-gray-100 text-gray-500'}`}>
          {icon}
        </div>
      )}
      <div>
        <h4 className="text-base font-semibold text-gray-800">{label}</h4>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
    </div>
    
    <div className="flex items-center">
      <div className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        isOn ? 'bg-pink-600' : 'bg-gray-300'
      }`}>
        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          isOn ? 'translate-x-6' : 'translate-x-1'
        }`} />
      </div>
      {loading && (
        <div className="ml-3 animate-spin w-4 h-4 border-2 border-pink-500 border-t-transparent rounded-full"></div>
      )}
    </div>
  </div>
);

const ActionButton = ({ icon, label, description, onClick, bgColor, textColor }) => (
  <div 
    className={`flex items-center gap-4 p-4 rounded-2xl border-2 border-transparent hover:border-pink-200 transition-colors cursor-pointer ${bgColor}`}
    onClick={onClick}
  >
    <div className={`p-2 rounded-full ${textColor}`}>
      {icon}
    </div>
    <div>
      <h4 className={`text-base font-semibold ${textColor}`}>{label}</h4>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  </div>
);

export default SettingsPage;