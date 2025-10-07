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
        <div className="glass-effect rounded-3xl p-8 mb-6 shadow-xl animate-fadeIn">
          <div className="flex items-center gap-4 mb-6">
            <img
              src={profile?.profileImage || "https://via.placeholder.com/80"}
              alt={profile?.username}
              className="w-20 h-20 rounded-full object-cover border-4 border-pink-200 shadow-lg"
            />
            <div>
              <h2 className="text-2xl font-bold text-gray-800">{profile?.fullName}</h2>
              <p className="text-lg text-gray-600">@{profile?.username}</p>
            </div>
          </div>

          {/* Privacy Setting */}
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-gray-800">Account Privacy</h3>
            
            <div 
              className="flex items-center justify-between p-6 bg-white rounded-2xl border-2 border-pink-100 hover:border-pink-200 transition-colors cursor-pointer"
              onClick={handlePrivacyToggle}
              data-testid="privacy-toggle"
            >
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-full ${isPrivate ? 'bg-purple-100' : 'bg-green-100'}`}>
                  {isPrivate ? (
                    <Shield className="w-6 h-6 text-purple-600" />
                  ) : (
                    <ShieldCheck className="w-6 h-6 text-green-600" />
                  )}
                </div>
                <div>
                  <h4 className="text-lg font-semibold text-gray-800">
                    {isPrivate ? 'Private Account' : 'Public Account'}
                  </h4>
                  <p className="text-sm text-gray-600">
                    {isPrivate 
                      ? 'Only followers you approve can see your posts and stories'
                      : 'Anyone can see your posts and stories'
                    }
                  </p>
                </div>
              </div>
              
              <div className="flex items-center">
                <div className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                  isPrivate ? 'bg-purple-600' : 'bg-gray-300'
                }`}>
                  <span className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                    isPrivate ? 'translate-x-7' : 'translate-x-1'
                  }`} />
                </div>
                {updating && (
                  <div className="ml-3 animate-spin w-5 h-5 border-2 border-pink-500 border-t-transparent rounded-full"></div>
                )}
              </div>
            </div>

            <div className="bg-pink-50 rounded-2xl p-4">
              <p className="text-sm text-gray-700">
                <strong>Note:</strong> When your account is private, new followers will need your approval. 
                Your current followers will still be able to see your content.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;