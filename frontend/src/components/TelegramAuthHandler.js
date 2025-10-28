import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { isTelegramWebApp, getTelegramInitData, expandTelegramWebApp } from '../utils/telegramWebApp';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TelegramAuthHandler = ({ onAuthSuccess }) => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleTelegramAuth = async () => {
      if (!isTelegramWebApp()) {
        console.log('Not running in Telegram WebApp');
        return;
      }

      console.log('✅ Telegram WebApp detected');
      expandTelegramWebApp();

      const initData = getTelegramInitData();
      
      if (!initData) {
        console.error('No initData available');
        return;
      }

      try {
        console.log('🔐 Authenticating with Telegram WebApp...');
        
        const formData = new FormData();
        formData.append('initData', initData);
        
        const response = await axios.post(`${API}/auth/telegram-webapp`, formData);
        
        if (response.data.success) {
          console.log('✅ Telegram authentication successful');
          
          // Store token
          localStorage.setItem('token', response.data.access_token);
          localStorage.setItem('user', JSON.stringify(response.data.user));
          
          // Call success callback
          if (onAuthSuccess) {
            onAuthSuccess(response.data.user);
          }
          
          // Navigate to home
          navigate('/home');
        }
      } catch (error) {
        console.error('❌ Telegram authentication failed:', error);
        console.error('Error details:', error.response?.data);
      }
    };

    handleTelegramAuth();
  }, [navigate, onAuthSuccess]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-600 mx-auto mb-4"></div>
        <p className="text-gray-600 text-lg">Authenticating with Telegram...</p>
        <p className="text-gray-500 text-sm mt-2">Please wait</p>
      </div>
    </div>
  );
};

export default TelegramAuthHandler;
