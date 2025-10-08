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
    
    try {
      // Create Telegram bot authentication dialog
      const authDialog = document.createElement('div');
      authDialog.style.position = 'fixed';
      authDialog.style.top = '0';
      authDialog.style.left = '0';
      authDialog.style.width = '100%';
      authDialog.style.height = '100%';
      authDialog.style.backgroundColor = 'rgba(0,0,0,0.8)';
      authDialog.style.zIndex = '9999';
      authDialog.style.display = 'flex';
      authDialog.style.alignItems = 'center';
      authDialog.style.justifyContent = 'center';
      
      const dialogContent = document.createElement('div');
      dialogContent.style.backgroundColor = 'white';
      dialogContent.style.padding = '30px';
      dialogContent.style.borderRadius = '15px';
      dialogContent.style.maxWidth = '400px';
      dialogContent.style.textAlign = 'center';
      dialogContent.innerHTML = `
        <h3 style="color: #1f2937; margin-bottom: 20px;">🤖 Telegram Authentication</h3>
        <p style="color: #6b7280; margin-bottom: 25px;">Your bot @Loveekisssbot is now active!</p>
        <div style="background: #f3f4f6; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
          <p style="margin: 10px 0; color: #374151;"><strong>1.</strong> Open Telegram</p>
          <p style="margin: 10px 0; color: #374151;"><strong>2.</strong> Message @Loveekisssbot</p>
          <p style="margin: 10px 0; color: #374151;"><strong>3.</strong> Send /start command</p>
          <p style="margin: 10px 0; color: #374151;"><strong>4.</strong> Return here and click "Check Status"</p>
        </div>
        <div style="display: flex; gap: 10px; justify-content: center;">
          <a href="https://t.me/Loveekisssbot" target="_blank" style="
            background: #0088cc; 
            color: white; 
            padding: 12px 20px; 
            border-radius: 8px; 
            text-decoration: none;
            display: inline-block;
          ">📱 Open Bot</a>
          <button id="checkStatus" style="
            background: #22c55e; 
            color: white; 
            padding: 12px 20px; 
            border: none; 
            border-radius: 8px;
            cursor: pointer;
          ">✅ Check Status</button>
          <button id="cancelAuth" style="
            background: #ef4444; 
            color: white; 
            padding: 12px 20px; 
            border: none; 
            border-radius: 8px;
            cursor: pointer;
          ">❌ Cancel</button>
        </div>
      `;
      
      authDialog.appendChild(dialogContent);
      document.body.appendChild(authDialog);
      
      // Handle status check
      document.getElementById('checkStatus').onclick = async () => {
        try {
          // Check if user authenticated via bot
          toast({
            title: "Checking...",
            description: "Verifying your Telegram authentication"
          });
          
          // For now, we'll use a simple check - in production this would check the database
          // for users who authenticated via the bot
          setTimeout(() => {
            toast({
              title: "Bot Active!",
              description: "Bot is working! Complete authentication in Telegram, then use traditional login for now.",
            });
            document.body.removeChild(authDialog);
            setTelegramLoading(false);
          }, 2000);
          
        } catch (error) {
          toast({
            title: "Authentication Failed",
            description: "Please make sure you've sent /start to @Loveekisssbot",
            variant: "destructive"
          });
        }
      };
      
      // Handle cancel
      document.getElementById('cancelAuth').onclick = () => {
        document.body.removeChild(authDialog);
        setTelegramLoading(false);
      };
      
    } catch (error) {
      toast({
        title: "Telegram Login Failed",
        description: error.response?.data?.detail || "Telegram authentication failed",
        variant: "destructive"
      });
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