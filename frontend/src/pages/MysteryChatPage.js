import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const MysteryChatPage = () => {
  const { matchId } = useParams();
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);
  
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [chatData, setChat​Data] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [showUnlock, setShowUnlock] = useState(null);
  
  const userId = localStorage.getItem('telegram_user_id') || localStorage.getItem('user_id');

  useEffect(() => {
    if (!userId) {
      navigate('/login');
      return;
    }
    fetchChat();
    const interval = setInterval(fetchChat, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [matchId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchChat = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/mystery/chat/${matchId}?user_id=${userId}`);
      if (response.data.success) {
        setMessages(response.data.messages);
        setChatData(response.data);
      }
    } catch (error) {
      console.error('Error fetching chat:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!messageText.trim()) return;
    
    setSending(true);
    
    try {
      const response = await axios.post(`${API_URL}/api/mystery/send-message`, {
        match_id: parseInt(matchId),
        sender_id: parseInt(userId),
        message_text: messageText
      });
      
      if (response.data.success) {
        setMessageText('');
        
        // Check if unlock achieved
        if (response.data.unlock_achieved) {
          setShowUnlock(response.data.unlock_achieved);
          setTimeout(() => setShowUnlock(null), 3000);
        }
        
        // Refresh chat
        fetchChat();
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message');
    } finally {
      setSending(false);
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
        <div className="text-white text-2xl">Loading chat...</div>
      </div>
    );
  }

  if (!chatData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-500 via-pink-500 to-red-500 flex items-center justify-center">
        <div className="text-white text-center">
          <div className="text-6xl mb-4">😕</div>
          <div className="text-2xl">Chat not found</div>
          <button
            onClick={() => navigate('/mystery')}
            className="mt-4 bg-white text-purple-600 px-6 py-2 rounded-full font-bold"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const partner = chatData.partner || {};
  const unlockLevel = chatData.unlock_level || 0;
  const messageCount = chatData.message_count || 0;
  const nextUnlock = [10, 30, 50, 100][unlockLevel];

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-purple-500 via-pink-500 to-red-500">
      {/* Header */}
      <div className="bg-white bg-opacity-10 backdrop-blur-md border-b border-white border-opacity-20 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => navigate('/mystery')}
              className="text-white hover:text-pink-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            
            {/* Partner Avatar */}
            <div className="relative">
              {partner.photo_url && unlockLevel >= 2 ? (
                <img
                  src={partner.photo_url}
                  alt="Mystery User"
                  className="w-10 h-10 rounded-full object-cover"
                  style={{
                    filter: `blur(${partner.photo_blur || 0}px)`
                  }}
                />
              ) : (
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-lg">
                  🎭
                </div>
              )}
              <div className="absolute -bottom-1 -right-1 bg-purple-500 rounded-full w-5 h-5 flex items-center justify-center text-xs text-white font-bold">
                {unlockLevel}
              </div>
            </div>

            {/* Partner Info */}
            <div>
              <div className="text-white font-bold">
                {partner.age ? `${partner.age}yo from ${partner.city || 'Unknown'}` : 'Mystery User'}
              </div>
              <div className="text-white text-opacity-75 text-xs">
                {nextUnlock ? `${messageCount}/${nextUnlock} to unlock` : 'Fully unlocked!'}
              </div>
            </div>
          </div>

          <div className="text-white text-sm text-right">
            <div className="font-semibold">⏰ {getTimeRemaining(chatData.expires_at)}</div>
            <div className="text-xs opacity-75">remaining</div>
          </div>
        </div>

        {/* Progress Bar */}
        {nextUnlock && (
          <div className="mt-2">
            <div className="bg-white bg-opacity-20 rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-gradient-to-r from-yellow-400 to-orange-500 h-full transition-all"
                style={{
                  width: `${(messageCount / nextUnlock) * 100}%`
                }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* Unlock Notification */}
      {showUnlock && (
        <div className="absolute top-20 left-1/2 transform -translate-x-1/2 z-50 animate-bounce">
          <div className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-6 py-3 rounded-full shadow-2xl">
            <div className="text-center">
              <div className="text-2xl mb-1">🎉</div>
              <div className="font-bold">New Unlock!</div>
              <div className="text-sm">{showUnlock.unlocked.join(', ')}</div>
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-white">
              <div className="text-6xl mb-4">💬</div>
              <div className="text-lg">Start the conversation!</div>
              <div className="text-sm opacity-75 mt-2">Say hi to your mystery match</div>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.is_me ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs md:max-w-md px-4 py-2 rounded-2xl ${
                  msg.is_me
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                    : 'bg-white bg-opacity-20 backdrop-blur-md text-white'
                }`}
              >
                <div>{msg.message}</div>
                <div className="text-xs opacity-75 mt-1">
                  {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Profile Preview (if unlocked) */}
      {unlockLevel > 0 && (
        <div className="bg-white bg-opacity-10 backdrop-blur-md border-t border-white border-opacity-20 px-4 py-2">
          <div className="text-white text-sm space-y-1">
            {partner.age && <div>📍 {partner.age} years old, {partner.city}</div>}
            {partner.interests && <div>💡 {partner.interests}</div>}
            {partner.bio && <div>✨ {partner.bio}</div>}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="bg-white bg-opacity-10 backdrop-blur-md border-t border-white border-opacity-20 px-4 py-3">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !sending && sendMessage()}
            placeholder="Type your message..."
            className="flex-1 bg-white bg-opacity-20 text-white placeholder-white placeholder-opacity-50 rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50"
          />
          <button
            onClick={sendMessage}
            disabled={sending || !messageText.trim()}
            className="bg-gradient-to-r from-pink-500 to-purple-600 text-white p-3 rounded-full hover:scale-110 transition-transform disabled:opacity-50 disabled:scale-100"
          >
            {sending ? (
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default MysteryChatPage;
