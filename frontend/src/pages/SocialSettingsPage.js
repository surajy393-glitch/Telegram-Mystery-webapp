import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Bell, Lock, Eye, Heart, MessageCircle } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SocialSettingsPage = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [settings, setSettings] = useState({
    privateProfile: false,
    allowAnonymousMessages: true,
    showOnlineStatus: true,
    allowStoryReplies: true,
    notifyOnLikes: true,
    notifyOnComments: true,
    notifyOnFollows: true,
  });
  const [loading, setLoading] = useState(true);

  // Fetch user settings on mount
  useEffect(() => {
    fetchUserSettings();
  }, []);

  const fetchUserSettings = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Map backend settings to frontend state
      setSettings({
        privateProfile: response.data.isPrivate || false,
        allowAnonymousMessages: response.data.allowDirectMessages !== false,
        showOnlineStatus: response.data.showOnlineStatus !== false,
        allowStoryReplies: response.data.allowStoryReplies !== false,
        notifyOnLikes: response.data.pushNotifications !== false,
        notifyOnComments: response.data.pushNotifications !== false,
        notifyOnFollows: response.data.pushNotifications !== false,
      });
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (key) => {
    const newValue = !settings[key];
    
    // Optimistically update UI
    setSettings({ ...settings, [key]: newValue });
    
    try {
      const token = localStorage.getItem('token');
      
      // Map frontend setting key to backend setting key
      const settingMap = {
        privateProfile: 'isPrivate',
        allowAnonymousMessages: 'allowDirectMessages',
        showOnlineStatus: 'showOnlineStatus',
        allowStoryReplies: 'allowStoryReplies',
        notifyOnLikes: 'pushNotifications',
        notifyOnComments: 'pushNotifications',
        notifyOnFollows: 'pushNotifications',
      };
      
      const backendKey = settingMap[key];
      
      // Save to backend
      await axios.put(`${API}/auth/settings`, 
        { [backendKey]: newValue },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      console.log(`Setting ${key} updated to ${newValue}`);
    } catch (error) {
      console.error('Error updating setting:', error);
      // Revert on error
      setSettings({ ...settings, [key]: !newValue });
      alert('Failed to update settings. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-4 border-pink-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-3 flex items-center space-x-3">
          <button
            onClick={() => navigate(-1)}
            className="text-gray-600 hover:text-pink-600"
          >
            <ArrowLeft size={24} />
          </button>
          <h1 className="text-xl font-bold">Social Settings</h1>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* Privacy Settings */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Lock className="text-pink-600" size={24} />
            <h2 className="text-lg font-semibold">Privacy</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Private Profile</h3>
                <p className="text-sm text-gray-500">Only followers can see your posts</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.privateProfile}
                  onChange={() => handleToggle('privateProfile')}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Show Online Status</h3>
                <p className="text-sm text-gray-500">Let others see when you're active</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.showOnlineStatus}
                  onChange={() => handleToggle('showOnlineStatus')}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Posts & Stories */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Eye className="text-pink-600" size={24} />
            <h2 className="text-lg font-semibold">Posts & Stories</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Allow Story Replies</h3>
                <p className="text-sm text-gray-500">Anyone can reply to your stories</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.allowStoryReplies}
                  onChange={() => handleToggle('allowStoryReplies')}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Anonymous Messages</h3>
                <p className="text-sm text-gray-500">Receive anonymous messages</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.allowAnonymousMessages}
                  onChange={() => handleToggle('allowAnonymousMessages')}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Bell className="text-pink-600" size={24} />
            <h2 className="text-lg font-semibold">Notifications</h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Heart size={20} className="text-gray-400" />
                <div>
                  <h3 className="font-medium">Likes</h3>
                  <p className="text-sm text-gray-500">When someone likes your post</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notifyOnLikes}
                  onChange={() => handleToggle('notifyOnLikes')}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <MessageCircle size={20} className="text-gray-400" />
                <div>
                  <h3 className="font-medium">Comments</h3>
                  <p className="text-sm text-gray-500">When someone comments</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notifyOnComments}
                  onChange={() => handleToggle('notifyOnComments')}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <User size={20} className="text-gray-400" />
                <div>
                  <h3 className="font-medium">New Followers</h3>
                  <p className="text-sm text-gray-500">When someone follows you</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notifyOnFollows}
                  onChange={() => handleToggle('notifyOnFollows')}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Mystery Match Settings Link */}
        <div className="bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg shadow-sm p-6 text-white">
          <h2 className="text-lg font-semibold mb-2">Mystery Match Settings</h2>
          <p className="text-sm text-white/80 mb-4">
            Configure your mystery match preferences separately
          </p>
          <button
            onClick={() => navigate('/settings')}
            className="bg-white text-purple-600 px-6 py-2 rounded-lg font-semibold hover:bg-gray-100"
          >
            Go to Mystery Match Settings
          </button>
        </div>

        {/* Logout */}
        <button
          onClick={onLogout}
          className="w-full py-3 bg-red-500 text-white rounded-lg font-semibold hover:bg-red-600"
        >
          Logout
        </button>
      </div>
    </div>
  );
};

export default SocialSettingsPage;
