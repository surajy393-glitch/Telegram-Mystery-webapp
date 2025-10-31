import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Bell, Lock, Eye, Heart, MessageCircle, Zap } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import axios from 'axios';

const API = "/api";

const SocialSettingsPage = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const BOT_USERNAME = process.env.REACT_APP_TELEGRAM_BOT_USERNAME || 'LuvHiveBot';
  const PREMIUM_INVOICE_SLUG = process.env.REACT_APP_PREMIUM_INVOICE_SLUG || 'luvhive_premium_month';
  const [premiumDialogOpen, setPremiumDialogOpen] = useState(false);
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

  const handleBuyPremiumStars = () => {
    // If the app runs inside Telegram Web/Mini App, use openInvoice
    if (
      window.Telegram &&
      window.Telegram.WebApp &&
      typeof window.Telegram.WebApp.openInvoice === "function"
    ) {
      window.Telegram.WebApp.openInvoice(PREMIUM_INVOICE_SLUG, (status) => {
        // Optional: refresh premium status on success
        if (status === 'paid') {
          console.log('✅ Premium payment successful!');
          // Optionally refresh user data to update premium status
          window.location.reload();
        } else if (status === 'cancelled') {
          console.log('❌ Premium payment cancelled');
        }
      });
    } else {
      // Fallback: open your bot to handle payment
      window.location.href = `https://t.me/${BOT_USERNAME}?start=premium_web`;
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
        {/* LuvHive Verified Button */}
        <button
          onClick={() => navigate('/verification-status')}
          className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white rounded-lg shadow-md p-4 flex items-center justify-between transition-all"
        >
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="text-left">
              <h3 className="font-semibold text-lg">LuvHive Verified</h3>
              <p className="text-sm text-blue-100">Get your verification badge</p>
            </div>
          </div>
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>

        {/* Premium Button */}
        <button
          onClick={() => setPremiumDialogOpen(true)}
          className="w-full bg-white border border-pink-200 rounded-lg shadow-md p-4 flex items-center justify-between hover:bg-pink-50 transition"
        >
          <div className="flex items-center space-x-3">
            <Zap className="text-pink-600" size={24} />
            <div className="text-left">
              <h3 className="font-semibold text-lg text-gray-800">Premium</h3>
              <p className="text-sm text-pink-600">See benefits & pricing</p>
            </div>
          </div>
          <svg className="w-5 h-5 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>

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

        {/* Logout */}
        <button
          onClick={onLogout}
          className="w-full py-3 bg-red-500 text-white rounded-lg font-semibold hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      {/* Premium Dialog */}
      <Dialog open={premiumDialogOpen} onOpenChange={setPremiumDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="mb-2">Premium Membership</DialogTitle>
            <DialogDescription>
              Compare what you get with Free vs Premium, then upgrade if you'd like.
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4 space-y-4">
            <div>
              <h3 className="font-semibold">Free</h3>
              <ul className="list-disc ml-5 text-sm text-gray-700 space-y-1">
                <li>View profiles, posts & stories</li>
                <li>Follow, like & comment</li>
                <li>Reply to messages unlimited</li>
                <li>Start 2 chats per day (20 messages total), text‑only</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold">Premium</h3>
              <ul className="list-disc ml-5 text-sm text-gray-700 space-y-1">
                <li>Start unlimited conversations</li>
                <li>Send photos, videos & voice notes</li>
                <li>Read receipts & typing indicators</li>
                <li>Priority placement in message requests</li>
                <li>Use gender, age & city filters in anonymous chat (Telegram bot)</li>
              </ul>
            </div>
            <div className="flex flex-col sm:flex-row sm:space-x-3 space-y-2 sm:space-y-0">
              {/* Replace anchor with button and call our handler */}
              <button
                onClick={handleBuyPremiumStars}
                className="flex-1 bg-gradient-to-r from-pink-500 to-pink-600 hover:from-pink-600 hover:to-pink-700 text-white py-2 px-4 rounded-md text-center"
              >
                Buy Premium with Stars
              </button>
              {/* Keep the fallback anchor for manual Telegram opening */}
              <a
                href={`https://t.me/${BOT_USERNAME}?start=premium_web`}
                target="_blank"
                rel="noreferrer"
                className="flex-1 border border-pink-500 text-pink-600 py-2 px-4 rounded-md text-center"
              >
                Open in Telegram
              </a>
            </div>
            <p className="text-xs text-gray-400">
              Prices start from <strong>250 Stars ($3.99)</strong> for 1 month.
              Payments are processed via Telegram Stars. Premium status syncs across both bot and webapp.
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default SocialSettingsPage;
