import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "@/pages/LandingPage";
import DatingRegisterPage from "@/pages/DatingRegisterPage";
import LoginPage from "@/pages/LoginPage";
import HomePage from "@/pages/HomePage";
import ProfilePage from "@/pages/ProfilePage";
import MyProfilePage from "@/pages/MyProfilePage";
import FeedPage from "@/pages/FeedPage";
import StoriesPage from "@/pages/StoriesPage";
import SocialSettingsPage from "@/pages/SocialSettingsPage";
import EditProfilePage from "@/pages/EditProfilePage";
import SettingsPage from "@/pages/SettingsPage";
import VerificationStatusPage from "@/pages/VerificationStatusPage";
import NotificationsPage from "@/pages/NotificationsPage";
import SearchPage from "@/pages/SearchPage";
import PostDetailPage from "@/pages/PostDetailPage";
import ChatPage from "@/pages/ChatPage";
import TelegramAuthHandler from "@/components/TelegramAuthHandler";
import { Toaster } from "@/components/ui/toaster";
import { getToken, getUser, setToken, setUser, clearAuth, getTelegramUserId } from "@/utils/telegramStorage";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get Telegram user ID to create isolated storage
    const getTelegramUserId = () => {
      try {
        if (window.Telegram?.WebApp?.initDataUnsafe?.user?.id) {
          return window.Telegram.WebApp.initDataUnsafe.user.id;
        }
      } catch (e) {
        console.log("Not in Telegram WebApp context");
      }
      return 'default';
    };

    const telegramUserId = getTelegramUserId();
    const storagePrefix = `tg_${telegramUserId}_`;
    
    console.log("🔍 App.js: Checking authentication for Telegram User ID:", telegramUserId);
    
    // Check if user is authenticated - use Telegram-user-specific keys
    const token = localStorage.getItem(`${storagePrefix}token`);
    const userDataString = localStorage.getItem(`${storagePrefix}user`);
    
    console.log("   Token present:", !!token);
    console.log("   User data present:", !!userDataString);
    
    if (token && userDataString) {
      try {
        const userData = JSON.parse(userDataString);
        console.log("✅ User loaded from localStorage:", userData.username);
        console.log("   Profile Image:", userData.profileImage);
        setIsAuthenticated(true);
        setUser(userData);
      } catch (error) {
        console.error("❌ Failed to parse user data:", error);
        localStorage.removeItem(`${storagePrefix}token`);
        localStorage.removeItem(`${storagePrefix}user`);
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (token, userData) => {
    console.log("🔐 handleLogin called with user:", userData);
    
    // Get Telegram user ID for isolated storage
    const getTelegramUserId = () => {
      try {
        if (window.Telegram?.WebApp?.initDataUnsafe?.user?.id) {
          return window.Telegram.WebApp.initDataUnsafe.user.id;
        }
      } catch (e) {
        console.log("Not in Telegram WebApp context");
      }
      return 'default';
    };

    const telegramUserId = getTelegramUserId();
    const storagePrefix = `tg_${telegramUserId}_`;
    
    console.log("   Storing with Telegram User ID:", telegramUserId);
    localStorage.setItem(`${storagePrefix}token`, token);
    localStorage.setItem(`${storagePrefix}user`, JSON.stringify(userData));
    setIsAuthenticated(true);
    setUser(userData);
    console.log("✅ User state updated, profileImage:", userData?.profileImage);
  };

  const handleLogout = () => {
    // Get Telegram user ID for isolated storage
    const getTelegramUserId = () => {
      try {
        if (window.Telegram?.WebApp?.initDataUnsafe?.user?.id) {
          return window.Telegram.WebApp.initDataUnsafe.user.id;
        }
      } catch (e) {
        console.log("Not in Telegram WebApp context");
      }
      return 'default';
    };

    const telegramUserId = getTelegramUserId();
    const storagePrefix = `tg_${telegramUserId}_`;
    
    console.log("🚪 Logging out Telegram User ID:", telegramUserId);
    localStorage.removeItem(`${storagePrefix}token`);
    localStorage.removeItem(`${storagePrefix}user`);
    setIsAuthenticated(false);
    setUser(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-pink-50 to-white">
        <div className="text-2xl text-pink-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          {/* Telegram WebApp Auth Route */}
          <Route 
            path="/telegram-auth" 
            element={
              <TelegramAuthHandler onAuthSuccess={handleLogin} />
            } 
          />
          <Route 
            path="/" 
            element={
              isAuthenticated ? (
                <Navigate to="/feed" replace />
              ) : (
                <LandingPage />
              )
            } 
          />
          <Route 
            path="/register" 
            element={
              isAuthenticated ? (
                <Navigate to="/feed" replace />
              ) : (
                <DatingRegisterPage onLogin={handleLogin} />
              )
            } 
          />
          <Route 
            path="/login" 
            element={
              isAuthenticated ? (
                <Navigate to="/feed" replace />
              ) : (
                <LoginPage onLogin={handleLogin} />
              )
            } 
          />
          <Route 
            path="/home" 
            element={<Navigate to="/feed" replace />}
          />
          <Route 
            path="/feed" 
            element={
              isAuthenticated ? (
                <FeedPage user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/stories" 
            element={
              isAuthenticated ? (
                <StoriesPage user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/social-settings" 
            element={
              isAuthenticated ? (
                <SocialSettingsPage user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/my-profile" 
            element={
              isAuthenticated ? (
                <MyProfilePage user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/edit-profile" 
            element={
              isAuthenticated ? (
                <EditProfilePage user={user} onLogin={handleLogin} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/settings" 
            element={
              isAuthenticated ? (
                <SettingsPage user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/verification-status" 
            element={
              isAuthenticated ? (
                <VerificationStatusPage user={user} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/notifications" 
            element={
              isAuthenticated ? (
                <NotificationsPage user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/search" 
            element={
              isAuthenticated ? (
                <SearchPage user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/post/:postId" 
            element={
              isAuthenticated ? (
                <PostDetailPage user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/profile/:userId" 
            element={
              isAuthenticated ? (
                <ProfilePage user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/chat/:userId" 
            element={
              isAuthenticated ? (
                <ChatPage user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;