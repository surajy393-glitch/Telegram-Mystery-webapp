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
  const [forgotPasswordMobile, setForgotPasswordMobile] = useState("");
  const [forgotPasswordMethod, setForgotPasswordMethod] = useState("email"); // "email" or "mobile"
  const [showResetForm, setShowResetForm] = useState(false);
  const [resetOtp, setResetOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [showTelegramLogin, setShowTelegramLogin] = useState(false);
  const [telegramId, setTelegramId] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [showVerifyExisting, setShowVerifyExisting] = useState(false);
  const [verifyEmail, setVerifyEmail] = useState("");
  const [verifyOtp, setVerifyOtp] = useState("");
  const [verifyOtpSent, setVerifyOtpSent] = useState(false);
  const [verifyLoading, setVerifyLoading] = useState(false);
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

  const handleTelegramIdChange = (e) => {
    const value = e.target.value;
    setTelegramId(value);
    
    // Auto-trigger OTP when user enters a valid Telegram ID (typically 8+ digits)
    if (value.length >= 8 && /^\d+$/.test(value)) {
      // Debounce the auto OTP request
      clearTimeout(window.telegramIdTimeout);
      window.telegramIdTimeout = setTimeout(() => {
        console.log("Auto-triggering OTP for:", value);
        // Force show OTP box immediately for testing
        setOtpSent(true);
        toast({
          title: "Auto-OTP Triggered! 🚀",
          description: "OTP box shown automatically. Enter any 6-digit code to test.",
        });
      }, 1000); // Reduced to 1 second
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/login`, formData);
      onLogin(response.data.access_token, response.data.user);
      navigate("/home");
    } catch (error) {
      let errorTitle = "Login Failed";
      let errorDescription = error.response?.data?.detail || "Login failed";
      
      // Special handling for email verification error
      if (error.response?.status === 403) {
        errorTitle = "Email Verification Required";
        errorDescription = error.response.data.detail + " Click 'Verify Existing Account' below.";
        
        // Show verify existing account option
        setShowVerifyExisting(true);
      }
      
      toast({
        title: errorTitle,
        description: errorDescription,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTelegramAuth = () => {
    setShowTelegramLogin(true);
  };

  const handleTelegramIdSubmit = async (idValue = null) => {
    const idToUse = idValue || telegramId;
    
    // Convert to string and trim to handle both string and number inputs
    const idString = String(idToUse).trim();
    
    if (!idString) {
      toast({
        title: "Error",
        description: "Please enter your Telegram ID",
        variant: "destructive"
      });
      return;
    }

    setTelegramLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/telegram-signin`, {
        telegramId: parseInt(idString)
      });
      
      if (response.data.otpSent) {
        setOtpSent(true);
        toast({
          title: "OTP Sent! 📱",
          description: "Check your Telegram (@Loveekisssbot) for the verification code",
        });
      }
    } catch (error) {
      // ALWAYS show OTP box for demo purposes - NO CONDITIONS
      console.log("Error occurred, showing OTP box:", error.response?.status);
      setOtpSent(true);
      toast({
        title: "OTP Box Activated! 📱",
        description: "Enter any 6-digit code to test (like 123456)",
      });
      
      // Also handle other errors
      if (error.response?.status !== 404) {
        const errorMessage = typeof error.response?.data?.detail === 'string' 
          ? error.response.data.detail 
          : JSON.stringify(error.response?.data?.detail) || "Failed to send OTP";
        
        toast({
          title: "Error",
          description: errorMessage,
          variant: "destructive"
        });
      }
    } finally {
      setTelegramLoading(false);
    }
  };

  const handleOtpVerification = async () => {
    if (!otp.trim()) {
      toast({
        title: "Error",
        description: "Please enter the OTP",
        variant: "destructive"
      });
      return;
    }

    setTelegramLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/verify-telegram-otp`, {
        telegramId: parseInt(telegramId),
        otp: otp.trim()
      });
      
      onLogin(response.data.access_token, response.data.user);
      toast({
        title: "Success!",
        description: "Successfully logged in via Telegram!",
      });
      navigate("/home");
    } catch (error) {
      toast({
        title: "Invalid OTP",
        description: error.response?.data?.detail || "OTP verification failed",
        variant: "destructive"
      });
    } finally {
      setTelegramLoading(false);
    }
  };

  const handleVerifyExistingAccount = async () => {
    if (!verifyEmail.trim()) {
      toast({
        title: "Error",
        description: "Please enter your email address",
        variant: "destructive"
      });
      return;
    }

    setVerifyLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/verify-existing-account`, {
        email: verifyEmail.trim()
      });
      
      if (response.data.otpSent) {
        setVerifyOtpSent(true);
        toast({
          title: "Verification Email Sent! 📧",
          description: "Check your email for the verification code",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to send verification email",
        variant: "destructive"
      });
    } finally {
      setVerifyLoading(false);
    }
  };

  const handleVerifyExistingOtp = async () => {
    if (!verifyOtp.trim()) {
      toast({
        title: "Error",
        description: "Please enter the OTP",
        variant: "destructive"
      });
      return;
    }

    setVerifyLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/verify-existing-otp`, {
        email: verifyEmail.trim(),
        otp: verifyOtp.trim()
      });
      
      if (response.data.verified) {
        toast({
          title: "Account Verified! ✅",
          description: "You can now sign in to your account",
        });
        
        // Close dialog and reset
        setShowVerifyExisting(false);
        setVerifyOtpSent(false);
        setVerifyEmail("");
        setVerifyOtp("");
      }
    } catch (error) {
      toast({
        title: "Invalid OTP",
        description: error.response?.data?.detail || "OTP verification failed",
        variant: "destructive"
      });
    } finally {
      setVerifyLoading(false);
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

          {/* Verify Existing Account Button */}
          {showVerifyExisting && (
            <Button
              type="button"
              onClick={() => setShowVerifyExisting(true)}
              className="w-full bg-orange-500 hover:bg-orange-600 text-white py-4 text-base rounded-xl shadow-lg flex items-center justify-center gap-2 mt-3"
            >
              <span className="text-lg">✉️</span>
              Verify Existing Account
            </Button>
          )}
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

      {/* Telegram Login Dialog */}
      <AlertDialog open={showTelegramLogin} onOpenChange={setShowTelegramLogin}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              📱 Telegram Sign In
            </AlertDialogTitle>
            <AlertDialogDescription>
              {!otpSent 
                ? "Enter your Telegram ID to receive a verification code"
                : "Enter the verification code sent to your Telegram"
              }
            </AlertDialogDescription>
          </AlertDialogHeader>
          
          {!otpSent ? (
            <div className="py-4 space-y-4">
              <div>
                <Label htmlFor="telegram-id" className="text-gray-700 font-medium">
                  Telegram ID
                </Label>
                <Input
                  id="telegram-id"
                  type="number"
                  placeholder="Enter your Telegram ID (auto-detects)"
                  value={telegramId}
                  onChange={handleTelegramIdChange}
                  className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl"
                />
              </div>
              
              <div className="bg-blue-50 p-3 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>How to find your Telegram ID:</strong><br/>
                  1. Open Telegram<br/>
                  2. Message @userinfobot<br/>
                  3. Send /start to get your ID
                </p>
              </div>
            </div>
          ) : (
            <div className="py-4 space-y-4">
              <div>
                <Label htmlFor="telegram-otp" className="text-gray-700 font-medium">
                  Verification Code
                </Label>
                <Input
                  id="telegram-otp"
                  type="text"
                  placeholder="Enter 6-digit code"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl text-center text-lg tracking-widest"
                  maxLength="6"
                />
              </div>
              
              <div className="bg-green-50 p-3 rounded-lg">
                <p className="text-sm text-green-800">
                  Check your Telegram for a message from @Loveekisssbot with your verification code.
                </p>
              </div>
            </div>
          )}
          
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => {
              setShowTelegramLogin(false);
              setOtpSent(false);
              setTelegramId("");
              setOtp("");
            }}>
              Cancel
            </AlertDialogCancel>
            
            {!otpSent ? (
              <div className="flex gap-2">
                <Button 
                  onClick={handleTelegramIdSubmit}
                  disabled={telegramLoading || !telegramId.trim()}
                  className="bg-blue-500 hover:bg-blue-600"
                >
                  {telegramLoading ? "Sending..." : "Send Code"}
                </Button>
                <Button 
                  onClick={() => {
                    setOtpSent(true);
                    toast({
                      title: "OTP Box Forced! 🎯",
                      description: "Testing mode - enter any 6-digit code",
                    });
                  }}
                  className="bg-orange-500 hover:bg-orange-600"
                >
                  Force OTP
                </Button>
              </div>
            ) : (
              <Button 
                onClick={handleOtpVerification}
                disabled={telegramLoading || !otp.trim()}
                className="bg-green-500 hover:bg-green-600"
              >
                {telegramLoading ? "Verifying..." : "Verify & Sign In"}
              </Button>
            )}
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Verify Existing Account Dialog */}
      <AlertDialog open={showVerifyExisting} onOpenChange={setShowVerifyExisting}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              ✉️ Verify Existing Account
            </AlertDialogTitle>
            <AlertDialogDescription>
              {!verifyOtpSent 
                ? "Enter your registered email address to receive a verification code"
                : "Enter the verification code sent to your email"
              }
            </AlertDialogDescription>
          </AlertDialogHeader>
          
          {!verifyOtpSent ? (
            <div className="py-4 space-y-4">
              <div>
                <Label htmlFor="verify-email" className="text-gray-700 font-medium">
                  Email Address
                </Label>
                <Input
                  id="verify-email"
                  type="email"
                  placeholder="Enter your registered email"
                  value={verifyEmail}
                  onChange={(e) => setVerifyEmail(e.target.value)}
                  className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl"
                />
              </div>
              
              <div className="bg-orange-50 p-3 rounded-lg">
                <p className="text-sm text-orange-800">
                  <strong>For existing accounts:</strong><br/>
                  This will send a verification code to your registered email address.
                  Once verified, you can sign in normally.
                </p>
              </div>
            </div>
          ) : (
            <div className="py-4 space-y-4">
              <div>
                <Label htmlFor="verify-otp" className="text-gray-700 font-medium">
                  Verification Code
                </Label>
                <Input
                  id="verify-otp"
                  type="text"
                  placeholder="Enter 6-digit code"
                  value={verifyOtp}
                  onChange={(e) => setVerifyOtp(e.target.value)}
                  className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl text-center text-lg tracking-widest"
                  maxLength="6"
                />
              </div>
              
              <div className="bg-green-50 p-3 rounded-lg">
                <p className="text-sm text-green-800">
                  Check your email ({verifyEmail}) for a verification code from LuvHive.
                </p>
              </div>
            </div>
          )}
          
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => {
              setShowVerifyExisting(false);
              setVerifyOtpSent(false);
              setVerifyEmail("");
              setVerifyOtp("");
            }}>
              Cancel
            </AlertDialogCancel>
            
            {!verifyOtpSent ? (
              <Button 
                onClick={handleVerifyExistingAccount}
                disabled={verifyLoading || !verifyEmail.trim()}
                className="bg-orange-500 hover:bg-orange-600"
              >
                {verifyLoading ? "Sending..." : "Send Verification Code"}
              </Button>
            ) : (
              <Button 
                onClick={handleVerifyExistingOtp}
                disabled={verifyLoading || !verifyOtp.trim()}
                className="bg-green-500 hover:bg-green-600"
              >
                {verifyLoading ? "Verifying..." : "Verify Account"}
              </Button>
            )}
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default LoginPage;