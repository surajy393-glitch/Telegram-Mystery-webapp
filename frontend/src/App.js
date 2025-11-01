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
import { getToken, getUser, setToken, setUser as setStorageUser, clearAuth, getTelegramUserId } from "@/utils/telegramStorage";
import { createHttpClient } from "@/utils/authClient";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const telegramUserId = getTelegramUserId();
    console.log("🔍 App.js: Checking authentication for Telegram User ID:", telegramUserId);
    
    // Check if user is authenticated - use Telegram-user-specific keys
    const token = getToken();
    const userData = getUser();
    
    console.log("   Token present:", !!token);
    console.log("   User data present:", !!userData);
    
    if (token && userData) {
      console.log("✅ User loaded from localStorage:", userData.username);
      console.log("   Profile Image:", userData.profileImage);
      setIsAuthenticated(true);
      setUser(userData);
      
      // Auto-refresh user data from server to get latest isPremium status
      refreshUserData(token, userData);
      
      // Auto-link Telegram ID if user is in Telegram and telegramId is not set
      if (telegramUserId !== 'default' && !userData.telegramId) {
        console.log("🔗 Auto-linking Telegram ID:", telegramUserId);
        linkTelegramAccount(token, telegramUserId, userData);
      }
    }
    setLoading(false);
  }, []);

  // Function to refresh user data from server
  const refreshUserData = async (token, currentUser) => {
    try {
      const httpClient = createHttpClient();
      const response = await httpClient.get("/api/auth/me");
      
      if (response.data) {
        console.log("🔄 Refreshed user data from server:", response.data.username, "isPremium:", response.data.isPremium);
        
        // Update user data in storage and state with fresh data
        setStorageUser(response.data);
        setUser(response.data);
      }
    } catch (error) {
      console.error("⚠️ Failed to refresh user data:", error);
      // If we get 401, token is invalid - force logout
      if (error.response?.status === 401) {
        console.log("🚪 Token invalid - forcing logout");
        handleLogout();
      }
    }
  };


  // Function to auto-link Telegram account
  const linkTelegramAccount = async (token, telegramId, currentUser) => {
    try {
      const httpClient = createHttpClient();
      const response = await httpClient.post("/api/auth/link-telegram", {
        telegramId: parseInt(telegramId)
      });

      if (response.data) {
        console.log("✅ Telegram account linked successfully");
        
        // Update user data in storage and state
        const updatedUser = { ...currentUser, telegramId: parseInt(telegramId) };
        setStorageUser(updatedUser);
        setUser(updatedUser);
      }
    } catch (error) {
      console.error("❌ Error linking Telegram account:", error);
      // If we get 401, token is invalid - force logout
      if (error.response?.status === 401) {
        console.log("🚪 Token invalid during Telegram linking - forcing logout");
        handleLogout();
      }
    }
  };


  const handleLogin = (token, userData) => {
    const telegramUserId = getTelegramUserId();
    console.log("🔐 handleLogin called with user:", userData);
    console.log("   Storing for Telegram User ID:", telegramUserId);
    
    setToken(token);
    setStorageUser(userData);
    setIsAuthenticated(true);
    setUser(userData);
    console.log("✅ User state updated, profileImage:", userData?.profileImage);
  };

  const handleLogout = () => {
    const telegramUserId = getTelegramUserId();
    console.log("🚪 Logging out Telegram User ID:", telegramUserId);
    
    clearAuth();
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
