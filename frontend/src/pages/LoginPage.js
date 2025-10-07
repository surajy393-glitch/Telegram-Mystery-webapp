import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel } from "@/components/ui/alert-dialog";
import { useToast } from "@/hooks/use-toast";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LoginPage = ({ onLogin }) => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [telegramLoading, setTelegramLoading] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [forgotPasswordEmail, setForgotPasswordEmail] = useState("");
  const [formData, setFormData] = useState({
    username: "",
    password: ""
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/login`, formData);
      onLogin(response.data.access_token, response.data.user);
      navigate("/home");
    } catch (error) {
      toast({
        title: "Login Failed",
        description: error.response?.data?.detail || "Login failed",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTelegramAuth = async () => {
    setTelegramLoading(true);
    
    // Simulate Telegram authentication (in production, use real Telegram Login Widget)
    const mockTelegramData = {
      id: Math.floor(Math.random() * 1000000000),
      first_name: "Telegram",
      last_name: "User", 
      username: "tguser" + Math.floor(Math.random() * 1000),
      photo_url: "https://via.placeholder.com/150/0088cc/FFFFFF?text=TG",
      auth_date: Math.floor(Date.now() / 1000),
      hash: "demo_hash_" + Math.random().toString(36).substr(2, 9)
    };

    try {
      const response = await axios.post(`${API}/auth/telegram`, mockTelegramData);
      onLogin(response.data.access_token, response.data.user);
      toast({
        title: "Success!",
        description: "Successfully logged in with Telegram",
      });
      navigate("/home");
    } catch (error) {
      toast({
        title: "Telegram Login Failed",
        description: error.response?.data?.detail || "Telegram authentication failed",
        variant: "destructive"
      });
    } finally {
      setTelegramLoading(false);
    }
  };

  const handleForgotPassword = async () => {
    if (!forgotPasswordEmail.trim()) {
      toast({
        title: "Error",
        description: "Please enter your email address",
        variant: "destructive"
      });
      return;
    }

    try {
      const response = await axios.post(`${API}/auth/forgot-password`, {
        email: forgotPasswordEmail.trim()
      });
      
      toast({
        title: "Reset Link Sent",
        description: response.data.message + (response.data.reset_link ? `\n\nFor testing: Check console for reset link` : ''),
      });
      
      if (response.data.reset_link) {
        console.log("Password reset link (for testing):", response.data.reset_link);
      }
      
      setShowForgotPassword(false);
      setForgotPasswordEmail("");
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to send reset email",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-pink-100 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8 animate-fadeIn">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-rose-500 mb-2">
            Welcome Back
          </h1>
          <p className="text-gray-600">Sign in to LuvHive</p>
        </div>

        <div className="glass-effect rounded-3xl p-8 shadow-xl animate-scaleIn">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="username" className="text-gray-700 font-medium">Username</Label>
              <Input
                id="username"
                name="username"
                data-testid="login-username-input"
                type="text"
                placeholder="Enter your username"
                value={formData.username}
                onChange={handleChange}
                required
                className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl"
              />
            </div>

            <div>
              <Label htmlFor="password" className="text-gray-700 font-medium">Password</Label>
              <Input
                id="password"
                name="password"
                data-testid="login-password-input"
                type="password"
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
                required
                className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl"
              />
            </div>

            <Button 
              type="submit"
              data-testid="login-submit-btn"
              disabled={loading}
              className="w-full bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white py-6 rounded-xl text-lg btn-hover"
            >
              {loading ? "Signing In..." : "Sign In"}
            </Button>

          {/* Forgot Password Link */}
          <div className="text-center mt-4">
            <button
              type="button"
              onClick={() => setShowForgotPassword(true)}
              className="text-pink-600 hover:text-pink-700 text-sm font-medium"
            >
              Forgot your password?
            </button>
          </div>

          {/* OR Divider */}
          <div className="flex items-center my-6">
            <div className="flex-1 border-t border-gray-300"></div>
            <span className="px-4 text-gray-500 text-sm">or</span>
            <div className="flex-1 border-t border-gray-300"></div>
          </div>

          {/* Telegram Login Button */}
          <Button
            type="button"
            onClick={handleTelegramAuth}
            disabled={telegramLoading}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white py-6 text-lg rounded-xl shadow-lg flex items-center justify-center gap-2"
          >
            {telegramLoading ? (
              "Connecting..."
            ) : (
              <>
                <span className="text-xl">📱</span>
                Continue with Telegram
              </>
            )}
          </Button>
          </form>

          <div className="mt-6 text-center text-gray-600">
            <p>Don't have an account? <Link to="/register" className="text-pink-600 font-semibold hover:underline">Register Now</Link></p>
          </div>
        </div>

        <div className="mt-6 text-center">
          <Link to="/">
            <Button variant="ghost" className="text-gray-600 hover:text-pink-600">
              ← Back to Home
            </Button>
          </Link>
        </div>
      </div>

      {/* Forgot Password Dialog */}
      <AlertDialog open={showForgotPassword} onOpenChange={setShowForgotPassword}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Reset Password</AlertDialogTitle>
            <AlertDialogDescription>
              Enter your email address and we'll send you a link to reset your password.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="py-4">
            <Label htmlFor="forgot-email" className="text-gray-700 font-medium">Email Address</Label>
            <Input
              id="forgot-email"
              type="email"
              placeholder="Enter your email"
              value={forgotPasswordEmail}
              onChange={(e) => setForgotPasswordEmail(e.target.value)}
              className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl"
            />
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <Button onClick={handleForgotPassword} className="bg-pink-500 hover:bg-pink-600">
              Send Reset Link
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default LoginPage;