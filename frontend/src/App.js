import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "@/pages/LandingPage";
import DatingRegisterPage from "@/pages/DatingRegisterPage";
import LoginPage from "@/pages/LoginPage";
import MysteryMatchHome from "@/pages/MysteryMatchHome";
import MysteryChatPage from "@/pages/MysteryChatPage";
import HomePage from "@/pages/HomePage";
import ProfilePage from "@/pages/ProfilePage";
import MyProfilePage from "@/pages/MyProfilePage";
import FeedPage from "@/pages/FeedPage";
import StoriesPage from "@/pages/StoriesPage";
import SocialSettingsPage from "@/pages/SocialSettingsPage";
import EditProfilePage from "@/pages/EditProfilePage";
import SettingsPage from "@/pages/SettingsPage";
import NotificationsPage from "@/pages/NotificationsPage";
import SearchPage from "@/pages/SearchPage";
import ChatPage from "@/pages/ChatPage";
import { Toaster } from "@/components/ui/toaster";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem("token");
    if (token) {
      setIsAuthenticated(true);
      const userData = localStorage.getItem("user");
      if (userData) {
        setUser(JSON.parse(userData));
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (token, userData) => {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(userData));
    setIsAuthenticated(true);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
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
            path="/mystery" 
            element={
              isAuthenticated ? (
                <MysteryMatchHome user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/mystery-chat/:matchId" 
            element={
              isAuthenticated ? (
                <MysteryChatPage user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
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
                <EditProfilePage user={user} onLogout={handleLogout} />
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