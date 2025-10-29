import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { isTelegramWebApp, getTelegramInitData, expandTelegramWebApp } from '../utils/telegramWebApp';

const API = '/api';

const MysteryMatchHome = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [activeMatches, setActiveMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [finding, setFinding] = useState(false);
  const [error, setError] = useState('');
  const [authenticating, setAuthenticating] = useState(false);
  
  // Get user data from localStorage (set during login)
  const userData = JSON.parse(localStorage.getItem('user') || '{}');
  // Use tg_user_id first (Telegram), then id, then _id (MongoDB) as fallback
  const userId = userData.tg_user_id || userData.id || userData._id;

  // Handle Telegram WebApp authentication
  useEffect(() => {
    const handleTelegramAuth = async () => {
      // Check if running in Telegram WebApp
      await new Promise(resolve => setTimeout(resolve, 500)); // Wait for SDK
      
      if (!isTelegramWebApp()) {
        console.log('Not in Telegram WebApp');
        return;
      }

      // Check if already authenticated
      const token = localStorage.getItem('token');
      if (token) {
        console.log('Already authenticated');
        return;
      }

      console.log('✅ Telegram WebApp detected - auto authenticating');
      setAuthenticating(true);
      expandTelegramWebApp();

      const initData = getTelegramInitData();
      
      if (!initData) {
        console.error('No initData available');
        setAuthenticating(false);
        return;
      }

      try {
        const formData = new FormData();
        formData.append('initData', initData);
        
        const response = await axios.post(`${API}/auth/telegram-webapp`, formData);
        
        if (response.data.success) {
          console.log('✅ Auto-auth successful');
          localStorage.setItem('token', response.data.access_token);
          localStorage.setItem('user', JSON.stringify(response.data.user));
          setAuthenticating(false);
          setUser(response.data.user); // Update state instead of reload
          setLoading(false);
        }
      } catch (error) {
        console.error('❌ Auto-auth failed:', error);
        setAuthenticating(false);
        setLoading(false);
      }
    };

    handleTelegramAuth();
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const currentUserId = userData.tg_user_id || userData.id;
    
    if (!currentUserId || !token) {
      console.log('Waiting for authentication...');
      return;
    }
    
    console.log('User authenticated, fetching data...');
    fetchUserData();
    fetchStats();
    fetchMatches();
  }, [user]); // Re-run when user state changes

  const fetchUserData = async () => {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const currentUserId = userData.tg_user_id || userData.id;
    
    if (!currentUserId) return;
    
    try {
      const response = await axios.get(`${API}/users/${currentUserId}`);
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user:', error);
    }
  };

  const fetchStats = async () => {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const currentUserId = userData.tg_user_id || userData.id;
    
    if (!currentUserId) return;
    
    try {
      const response = await axios.get(`${API}/mystery/stats/${currentUserId}`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchMatches = async () => {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const currentUserId = userData.tg_user_id || userData.id;
    
    if (!currentUserId) return;
    
    try {
      const response = await axios.get(`${API}/mystery/my-matches/${currentUserId}`);
      setActiveMatches(response.data.matches || []);
    } catch (error) {
      console.error('Error fetching matches:', error);
    } finally {
      setLoading(false);
    }
  };

  const findMysteryMatch = async (preferredGender = 'random') => {
    setFinding(true);
    setError('');
    
    try {
      const response = await axios.post(`${API}/mystery/find-match`, {
        user_id: parseInt(userId),
        preferred_age_min: 18,
        preferred_age_max: 35,
        preferred_gender: preferredGender  // 'random', 'male', or 'female'
      });
      
      if (response.data.success) {
        // Navigate to chat with new match
        navigate(`/mystery-chat/${response.data.match_id}`);
      } else {
        // Show specific error message if gender not available
        setError(response.data.message || 'Failed to find match');
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Error finding match');
    } finally {
      setFinding(false);
    }
  };

  const getTimeRemaining = (expiresAt) => {
    const now = new Date();
    const expires = new Date(expiresAt);
    const diff = expires - now;
    
    if (diff < 0) return 'Expired';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours}h ${minutes}m`;
  };

  if (authenticating) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-500 via-pink-500 to-red-500 flex items-center justify-center">
        <div className="text-center text-white">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-white mx-auto mb-4"></div>
          <div className="text-2xl">Authenticating with Telegram...</div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-500 via-pink-500 to-red-500 flex items-center justify-center">
        <div className="text-white text-2xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-500 via-pink-500 to-red-500">
      {/* Header */}
      <div className="bg-white bg-opacity-10 backdrop-blur-md border-b border-white border-opacity-20">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/feed')}
              className="text-white hover:text-pink-200 transition p-2 hover:bg-white hover:bg-opacity-10 rounded-lg"
              title="Back to Feed"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <h1 className="text-2xl font-bold text-white">🎭 LuvHive Mystery Match</h1>
          </div>
          <button
            onClick={() => navigate('/settings')}
            className="text-white hover:text-pink-200 transition"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-2xl p-4 border border-white border-opacity-20">
              <div className="text-white text-opacity-80 text-sm mb-1">Total Matches</div>
              <div className="text-white text-3xl font-bold">{stats.total_matches}</div>
            </div>
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-2xl p-4 border border-white border-opacity-20">
              <div className="text-white text-opacity-80 text-sm mb-1">Active</div>
              <div className="text-white text-3xl font-bold">{stats.active_matches}</div>
            </div>
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-2xl p-4 border border-white border-opacity-20">
              <div className="text-white text-opacity-80 text-sm mb-1">Today</div>
              <div className="text-white text-3xl font-bold">
                {stats.today_matches}/{stats.is_premium ? '∞' : stats.daily_limit}
              </div>
            </div>
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-2xl p-4 border border-white border-opacity-20">
              <div className="text-white text-opacity-80 text-sm mb-1">Messages</div>
              <div className="text-white text-3xl font-bold">{stats.messages_sent}</div>
            </div>
          </div>
        )}

        {/* Premium Banner */}
        {stats && !stats.is_premium && (
          <div className="bg-gradient-to-r from-yellow-400 to-orange-500 rounded-2xl p-6 text-white shadow-2xl">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold mb-2">✨ Upgrade to Premium</h3>
                <p className="text-sm opacity-90 mb-2">👧 Choose Girls • 👦 Choose Boys • Unlimited matches • Instant reveals</p>
                <p className="text-lg font-bold mt-3 bg-white text-orange-600 inline-block px-4 py-2 rounded-lg">
                  🎁 Try 1 Week for Just ₹199! 🔥
                </p>
              </div>
              <button
                onClick={() => {
                  // Open Telegram bot and auto-send /premium command
                  window.open('https://t.me/Loveekisssbot?text=/premium', '_blank');
                }}
                className="bg-white text-orange-500 px-6 py-3 rounded-full font-bold hover:bg-opacity-90 transition shadow-lg hover:scale-105"
              >
                Upgrade Now
              </button>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-500 bg-opacity-20 backdrop-blur-md border border-red-400 rounded-2xl p-4 text-white">
            {error}
          </div>
        )}

        {/* Find Match Button - Free Users */}
        {!stats?.is_premium && (
          <button
            onClick={() => findMysteryMatch('random')}
            disabled={finding}
            className="w-full bg-gradient-to-r from-pink-500 to-purple-600 text-white py-6 rounded-2xl text-xl font-bold hover:scale-105 transition-transform disabled:opacity-50 disabled:scale-100 shadow-2xl"
          >
            {finding ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin h-6 w-6 mr-3" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Finding Random Match...
              </span>
            ) : (
              <div>
                <div className="text-2xl">🎲 Find Mystery Match</div>
                <div className="text-sm opacity-80 mt-1">Random matching • Could be anyone</div>
              </div>
            )}
          </button>
        )}

        {/* Find Match Buttons - Premium Users */}
        {stats?.is_premium && (
          <div className="space-y-4">
            <div className="bg-yellow-400 bg-opacity-20 backdrop-blur-md border border-yellow-400 border-opacity-40 rounded-2xl p-4 text-center">
              <span className="text-yellow-300 font-bold">👑 Premium Feature</span>
              <p className="text-white text-sm mt-1">Choose who you want to match with!</p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => findMysteryMatch('female')}
                disabled={finding}
                className="bg-gradient-to-br from-pink-400 to-rose-500 text-white py-8 rounded-2xl font-bold hover:scale-105 transition-transform disabled:opacity-50 disabled:scale-100 shadow-2xl"
              >
                {finding ? (
                  <div className="flex flex-col items-center">
                    <svg className="animate-spin h-6 w-6 mb-2" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span className="text-sm">Searching...</span>
                  </div>
                ) : (
                  <div>
                    <div className="text-4xl mb-2">👧</div>
                    <div className="text-lg">Find a Girl</div>
                  </div>
                )}
              </button>
              
              <button
                onClick={() => findMysteryMatch('male')}
                disabled={finding}
                className="bg-gradient-to-br from-blue-400 to-indigo-500 text-white py-8 rounded-2xl font-bold hover:scale-105 transition-transform disabled:opacity-50 disabled:scale-100 shadow-2xl"
              >
                {finding ? (
                  <div className="flex flex-col items-center">
                    <svg className="animate-spin h-6 w-6 mb-2" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span className="text-sm">Searching...</span>
                  </div>
                ) : (
                  <div>
                    <div className="text-4xl mb-2">👦</div>
                    <div className="text-lg">Find a Boy</div>
                  </div>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Active Matches */}
        <div className="space-y-4">
          <h2 className="text-white text-xl font-bold">💬 Active Chats ({activeMatches.length})</h2>
          
          {activeMatches.length === 0 ? (
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-2xl p-8 text-center text-white border border-white border-opacity-20">
              <div className="text-6xl mb-4">🎭</div>
              <p className="text-lg">No active matches yet</p>
              <p className="text-sm opacity-75 mt-2">Click "Find Mystery Match" to start!</p>
            </div>
          ) : (
            activeMatches.map(match => (
              <div
                key={match.match_id}
                onClick={() => navigate(`/mystery-chat/${match.match_id}`)}
                className="bg-white bg-opacity-10 backdrop-blur-md rounded-2xl p-4 cursor-pointer hover:bg-opacity-20 transition border border-white border-opacity-20"
              >
                <div className="flex items-center space-x-4">
                  {/* Mystery Avatar */}
                  <div className="relative">
                    {match.partner.photo_url && match.unlock_level >= 2 ? (
                      <img
                        src={match.partner.photo_url}
                        alt="Mystery User"
                        className="w-16 h-16 rounded-full object-cover"
                        style={{
                          filter: `blur(${match.partner.photo_blur || 0}px)`
                        }}
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-2xl">
                        🎭
                      </div>
                    )}
                    <div className="absolute -bottom-1 -right-1 bg-purple-500 rounded-full px-2 py-0.5 text-xs text-white font-bold">
                      {match.unlock_level}/4
                    </div>
                  </div>

                  {/* Match Info */}
                  <div className="flex-1">
                    <h3 className="text-white font-bold text-lg">
                      {match.partner.age ? `${match.partner.age}yo from ${match.partner.city || 'Unknown'}` : 'Mystery User'}
                    </h3>
                    <div className="text-white text-opacity-75 text-sm space-y-1">
                      <div>💬 {match.message_count} messages</div>
                      {match.next_unlock_at && (
                        <div>🔓 Next unlock: {match.next_unlock_at} messages</div>
                      )}
                      <div>⏰ {getTimeRemaining(match.expires_at)} remaining</div>
                    </div>
                  </div>

                  {/* Arrow */}
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>

                {/* Progress Bar */}
                {match.next_unlock_at && (
                  <div className="mt-3">
                    <div className="bg-white bg-opacity-20 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-yellow-400 to-orange-500 h-full transition-all"
                        style={{
                          width: `${(match.message_count / match.next_unlock_at) * 100}%`
                        }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* How It Works */}
        <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-2xl p-6 text-white border border-white border-opacity-20">
          <h3 className="text-lg font-bold mb-4">❓ How It Works</h3>
          <div className="space-y-3 text-sm">
            <div className="flex items-start space-x-3">
              <span className="text-2xl">🎭</span>
              <div>
                <div className="font-semibold">Mystery Matching</div>
                <div className="opacity-75">Get matched with someone new. Their profile is hidden at first!</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <span className="text-2xl">💬</span>
              <div>
                <div className="font-semibold">Chat to Unlock</div>
                <div className="opacity-75">Send messages to gradually reveal their profile</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <span className="text-2xl">🔓</span>
              <div>
                <div className="font-semibold">Progressive Reveal</div>
                <div className="opacity-75">20 msgs → Gender+Age | 60 → Photo | 100 → Interests | 150 → Full Profile</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <span className="text-2xl">⏰</span>
              <div>
                <div className="font-semibold">48-Hour Window</div>
                <div className="opacity-75">Each match expires in 48 hours. Make it count!</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MysteryMatchHome;
