import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const MysteryMatchHome = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [activeMatches, setActiveMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [finding, setFinding] = useState(false);
  const [error, setError] = useState('');
  
  const userId = localStorage.getItem('telegram_user_id') || localStorage.getItem('user_id');

  useEffect(() => {
    if (!userId) {
      navigate('/login');
      return;
    }
    fetchUserData();
    fetchStats();
    fetchMatches();
  }, [userId]);

  const fetchUserData = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/users/${userId}`);
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/mystery/stats/${userId}`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchMatches = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/mystery/my-matches/${userId}`);
      setActiveMatches(response.data.matches || []);
    } catch (error) {
      console.error('Error fetching matches:', error);
    } finally {
      setLoading(false);
    }
  };

  const findMysteryMatch = async () => {
    setFinding(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_URL}/api/mystery/find-match`, {
        user_id: parseInt(userId),
        preferred_age_min: 18,
        preferred_age_max: 35
      });
      
      if (response.data.success) {
        // Navigate to chat with new match
        navigate(`/mystery-chat/${response.data.match_id}`);
      } else {
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
          <h1 className="text-2xl font-bold text-white">🎭 Mystery Match</h1>
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
          <div className="bg-gradient-to-r from-yellow-400 to-orange-500 rounded-2xl p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold mb-2">✨ Upgrade to Premium</h3>
                <p className="text-sm opacity-90">Unlimited matches • See profiles instantly • Advanced filters</p>
                <p className="text-sm font-semibold mt-2">Only ₹100/month (250 Stars)</p>
              </div>
              <button
                onClick={() => window.open('https://t.me/Loveekisssbot?start=premium', '_blank')}
                className="bg-white text-orange-500 px-6 py-3 rounded-full font-bold hover:bg-opacity-90 transition"
              >
                Upgrade
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

        {/* Find Match Button */}
        <button
          onClick={findMysteryMatch}
          disabled={finding}
          className="w-full bg-gradient-to-r from-pink-500 to-purple-600 text-white py-6 rounded-2xl text-xl font-bold hover:scale-105 transition-transform disabled:opacity-50 disabled:scale-100 shadow-2xl"
        >
          {finding ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin h-6 w-6 mr-3" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Finding Mystery Match...
            </span>
          ) : (
            '🎲 Find Mystery Match'
          )}
        </button>

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
                <div className="opacity-75">10 msgs → Age+City | 30 → Photo | 50 → Interests | 100 → Full Profile</div>
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
