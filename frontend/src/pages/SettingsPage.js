import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Shield, ShieldCheck, Eye, EyeOff, Search, MessageCircle, Wifi, Tag, MessageSquare, Zap, Bell, BellOff, Mail, MailX, Download, HelpCircle, LogOut } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SettingsPage = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [settings, setSettings] = useState({
    // Privacy Controls
    isPrivate: false,
    publicProfile: true,
    appearInSearch: true,
    allowDirectMessages: true,
    showOnlineStatus: true,
    
    // Interaction Preferences
    allowTagging: true,
    allowStoryReplies: true,
    showVibeScore: true,
    
    // Notifications
    pushNotifications: true,
    emailNotifications: true
  });
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState({});

  useEffect(() => {
    fetchProfile();
  }, []);

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
        publicProfile: response.data.publicProfile !== false,
        appearInSearch: response.data.appearInSearch !== false,
        allowDirectMessages: response.data.allowDirectMessages !== false,
        showOnlineStatus: response.data.showOnlineStatus !== false,
        allowTagging: response.data.allowTagging !== false,
        allowStoryReplies: response.data.allowStoryReplies !== false,
        showVibeScore: response.data.showVibeScore !== false,
        pushNotifications: response.data.pushNotifications !== false,
        emailNotifications: response.data.emailNotifications !== false
      });
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

        {/* Account Privacy Section */}
        <div className="glass-effect rounded-3xl p-6 mb-6 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className={`p-3 rounded-full ${settings.isPrivate ? 'bg-purple-100' : 'bg-green-100'}`}>
              {settings.isPrivate ? (
                <Shield className="w-6 h-6 text-purple-600" />
              ) : (
                <ShieldCheck className="w-6 h-6 text-green-600" />
              )}
            </div>
            <h3 className="text-xl font-bold text-gray-800">
              {settings.isPrivate ? 'Private Account' : 'Public Account'}
            </h3>
          </div>
          
          <SettingToggle
            label="Private Account"
            description="Only approved followers can see your posts and stories"
            isOn={settings.isPrivate}
            onToggle={() => handleSettingToggle('isPrivate')}
            loading={updating.isPrivate}
          />
        </div>

        {/* Privacy Controls Section */}
        <div className="glass-effect rounded-3xl p-6 mb-6 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 rounded-full bg-yellow-100">
              <Shield className="w-6 h-6 text-yellow-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800">Privacy Controls</h3>
          </div>
          
          <div className="space-y-4">
            <SettingToggle
              icon={<Search className="w-5 h-5" />}
              label="Appear in Search"
              description="Let others discover you in search results"
              isOn={settings.appearInSearch}
              onToggle={() => handleSettingToggle('appearInSearch')}
              loading={updating.appearInSearch}
            />
            
            <SettingToggle
              icon={<MessageCircle className="w-5 h-5" />}
              label="Allow Direct Messages"
              description="Let other users send you private messages"
              isOn={settings.allowDirectMessages}
              onToggle={() => handleSettingToggle('allowDirectMessages')}
              loading={updating.allowDirectMessages}
            />
            
            <SettingToggle
              icon={<Wifi className="w-5 h-5" />}
              label="Show Online Status"
              description="Display when you're active on LuvHive"
              isOn={settings.showOnlineStatus}
              onToggle={() => handleSettingToggle('showOnlineStatus')}
              loading={updating.showOnlineStatus}
            />
          </div>
        </div>

        {/* Blocked Users Section */}
        <div className="glass-effect rounded-3xl p-6 mb-6 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 rounded-full bg-red-100">
              <Shield className="w-6 h-6 text-red-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800">Blocked Users</h3>
          </div>
          
          <ActionButton
            icon={<Shield className="w-5 h-5" />}
            label="Manage Blocked Users"
            description={`View and unblock users (${profile?.blockedUsers?.length || 0} blocked)`}
            onClick={() => setShowBlockedUsers(true)}
            bgColor="bg-red-50 hover:bg-red-100"
            textColor="text-red-600"
          />
        </div>

        {/* Interaction Preferences Section */}
        <div className="glass-effect rounded-3xl p-6 mb-6 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 rounded-full bg-blue-100">
              <Zap className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800">Interaction Preferences</h3>
          </div>
          
          <div className="space-y-4">
            <SettingToggle
              icon={<Tag className="w-5 h-5" />}
              label="Allow Tagging"
              description="Let others tag you in posts and stories"
              isOn={settings.allowTagging}
              onToggle={() => handleSettingToggle('allowTagging')}
              loading={updating.allowTagging}
            />
            
            <SettingToggle
              icon={<MessageSquare className="w-5 h-5" />}
              label="Story Replies"
              description="Allow others to reply to your stories"
              isOn={settings.allowStoryReplies}
              onToggle={() => handleSettingToggle('allowStoryReplies')}
              loading={updating.allowStoryReplies}
            />
            
            <SettingToggle
              icon={<Zap className="w-5 h-5" />}
              label="Show Vibe Score"
              description="Display your vibe compatibility score"
              isOn={settings.showVibeScore}
              onToggle={() => handleSettingToggle('showVibeScore')}
              loading={updating.showVibeScore}
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