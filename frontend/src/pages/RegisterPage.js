import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import axios from "axios";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RegisterPage = ({ onLogin }) => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [telegramLoading, setTelegramLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [usernameStatus, setUsernameStatus] = useState(null); // null, 'checking', 'available', 'taken'
  const [usernameSuggestions, setUsernameSuggestions] = useState([]);
  const [usernameMessage, setUsernameMessage] = useState("");
  const [emailStatus, setEmailStatus] = useState(null); // null, 'checking', 'available', 'taken'
  const [emailMessage, setEmailMessage] = useState("");
  const [emailOtpSent, setEmailOtpSent] = useState(false);
  const [emailOtp, setEmailOtp] = useState("");
  const [emailVerified, setEmailVerified] = useState(false);
  const [otpLoading, setOtpLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    fullName: "",
    username: "",
    email: "",
    mobileNumber: "",
    age: "",
    gender: "",
    password: "",
    bio: "",
    profileImage: ""
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Check username availability when username changes
    if (name === 'username') {
      checkUsernameAvailability(value);
    }
    
    // Check email availability when email changes
    if (name === 'email') {
      checkEmailAvailability(value);
    }
  };

  const checkUsernameAvailability = async (username) => {
    if (!username || username.length < 3) {
      setUsernameStatus(null);
      setUsernameSuggestions([]);
      setUsernameMessage("");
      return;
    }

    setUsernameStatus('checking');
    setUsernameMessage("Checking availability...");
    
    try {
      const response = await axios.get(`${API}/auth/check-username/${encodeURIComponent(username)}`);
      const data = response.data;
      
      if (data.available) {
        setUsernameStatus('available');
        setUsernameMessage(data.message);
        setUsernameSuggestions([]);
      } else {
        setUsernameStatus('taken');
        setUsernameMessage(data.message);
        setUsernameSuggestions(data.suggestions);
      }
    } catch (error) {
      setUsernameStatus('error');
      setUsernameMessage("Error checking username");
      setUsernameSuggestions([]);
    }
  };

  const selectSuggestion = (suggestion) => {
    setFormData({
      ...formData,
      username: suggestion
    });
    checkUsernameAvailability(suggestion);
  };

  const sendEmailOtp = async () => {
    if (!formData.email || emailStatus !== 'available') {
      toast({
        title: "Error",
        description: "Please enter a valid available email first",
        variant: "destructive"
      });
      return;
    }

    setOtpLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/send-email-otp`, {
        email: formData.email
      });
      
      if (response.data.otpSent) {
        setEmailOtpSent(true);
        toast({
          title: "OTP Sent! 📧",
          description: "Check your email for the verification code",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to send OTP",
        variant: "destructive"
      });
    } finally {
      setOtpLoading(false);
    }
  };

  const verifyEmailOtp = async () => {
    if (!emailOtp.trim()) {
      toast({
        title: "Error",
        description: "Please enter the OTP",
        variant: "destructive"
      });
      return;
    }

    setOtpLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/verify-email-otp`, {
        email: formData.email,
        otp: emailOtp.trim()
      });
      
      if (response.data.verified) {
        setEmailVerified(true);
        toast({
          title: "Email Verified! ✅",
          description: "You can now proceed to the next step",
        });
      }
    } catch (error) {
      toast({
        title: "Invalid OTP",
        description: error.response?.data?.detail || "OTP verification failed",
        variant: "destructive"
      });
    } finally {
      setOtpLoading(false);
    }
  };

  const checkEmailAvailability = async (email) => {
    if (!email || !email.includes('@')) {
      setEmailStatus(null);
      setEmailMessage("");
      return;
    }

    setEmailStatus('checking');
    setEmailMessage("Checking email...");
    
    try {
      const response = await axios.get(`${API}/auth/check-email/${encodeURIComponent(email)}`);
      const data = response.data;
      
      if (data.available) {
        setEmailStatus('available');
        setEmailMessage(data.message);
      } else {
        setEmailStatus('taken');
        setEmailMessage(data.message);
      }
    } catch (error) {
      setEmailStatus('error');
      setEmailMessage("Error checking email");
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData({
          ...formData,
          profileImage: reader.result
        });
      };
      reader.readAsDataURL(file);
    }
  };

  const handleStep1Submit = (e) => {
    e.preventDefault();
    
    if (formData.fullName && formData.username && formData.email && formData.age && formData.gender && formData.password) {
      setStep(2);
    }
  };

  const handleFinalSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // First register the user with enhanced endpoint
      const response = await axios.post(`${API}/auth/register-enhanced`, {
        fullName: formData.fullName,
        username: formData.username,
        email: formData.email,
        mobileNumber: formData.mobileNumber || null,
        age: parseInt(formData.age),
        gender: formData.gender,
        password: formData.password
      });

      // Check if email verification is required
      if (response.data.email_verification_required) {
        toast({
          title: "Check Your Email! 📧",
          description: response.data.message,
        });
        
        // Show success popup with email verification message
        setShowSuccess(true);
        setLoading(false);
        return;
      }

      const token = response.data.access_token;

      // Then update profile with bio and image
      if (formData.bio || formData.profileImage) {
        const formDataToSend = new FormData();
        if (formData.bio) formDataToSend.append("bio", formData.bio);
        if (formData.profileImage) formDataToSend.append("profileImage", formData.profileImage);

        await axios.put(`${API}/auth/profile`, formDataToSend, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data"
          }
        });
      }

      // Show success popup
      setShowSuccess(true);

      // Auto redirect after 2 seconds
      setTimeout(() => {
        onLogin(token, response.data.user);
        navigate("/home");
      }, 2000);
      
    } catch (error) {
      toast({
        title: "Registration Failed",
        description: error.response?.data?.detail || "Registration failed",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTelegramAuth = async () => {
    setTelegramLoading(true);
    
    try {
      // Show info about secure registration
      toast({
        title: "Secure Registration",
        description: "Creating account with Telegram authentication via @Loveekisssbot",
      });

      // Create a div to hold the Telegram Login Widget
      const widgetContainer = document.createElement('div');
      widgetContainer.id = 'telegram-register-widget';
      widgetContainer.style.position = 'fixed';
      widgetContainer.style.top = '50%';
      widgetContainer.style.left = '50%';
      widgetContainer.style.transform = 'translate(-50%, -50%)';
      widgetContainer.style.zIndex = '9999';
      widgetContainer.style.backgroundColor = 'white';
      widgetContainer.style.padding = '20px';
      widgetContainer.style.borderRadius = '10px';
      widgetContainer.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
      
      // Add close button
      const closeButton = document.createElement('button');
      closeButton.innerHTML = '×';
      closeButton.style.position = 'absolute';
      closeButton.style.top = '5px';
      closeButton.style.right = '10px';
      closeButton.style.background = 'none';
      closeButton.style.border = 'none';
      closeButton.style.fontSize = '20px';
      closeButton.style.cursor = 'pointer';
      closeButton.onclick = () => {
        document.body.removeChild(widgetContainer);
        setTelegramLoading(false);
      };
      
      widgetContainer.appendChild(closeButton);
      
      // Add title
      const title = document.createElement('h3');
      title.textContent = 'Register with Telegram';
      title.style.marginBottom = '15px';
      title.style.textAlign = 'center';
      widgetContainer.appendChild(title);

      // Create Telegram Login Widget script
      const telegramScript = document.createElement('script');
      telegramScript.async = true;
      telegramScript.src = 'https://telegram.org/js/telegram-widget.js?22';
      telegramScript.setAttribute('data-telegram-login', 'Loveekisssbot');
      telegramScript.setAttribute('data-size', 'large');
      telegramScript.setAttribute('data-radius', '10');
      telegramScript.setAttribute('data-request-access', 'write');
      telegramScript.setAttribute('data-onauth', 'onTelegramRegister(user)');
      
      widgetContainer.appendChild(telegramScript);
      document.body.appendChild(widgetContainer);

      // Global callback function for Telegram registration
      window.onTelegramRegister = async (user) => {
        try {
          // Remove widget
          if (document.getElementById('telegram-register-widget')) {
            document.body.removeChild(widgetContainer);
          }

          // First check if user already exists
          try {
            const checkResponse = await axios.post(`${API}/auth/telegram-signin`, {
              telegramId: user.id
            });
            
            // If we get here, user already exists - redirect to login
            toast({
              title: "Account Already Exists",
              description: "You already have an account! Please use the Login page with Telegram sign-in.",
              variant: "destructive"
            });
            
            // Redirect to login page after 2 seconds
            setTimeout(() => {
              navigate("/login");
            }, 2000);
            
            setTelegramLoading(false);
            return;
            
          } catch (error) {
            // If user doesn't exist (404 error), proceed with registration
            if (error.response?.status !== 404) {
              throw error; // Re-throw if it's a different error
            }
          }

          // User doesn't exist, proceed with registration
          const response = await axios.post(`${API}/auth/telegram`, {
            id: user.id,
            first_name: user.first_name,
            last_name: user.last_name || "",
            username: user.username || "",
            photo_url: user.photo_url || "",
            auth_date: user.auth_date,
            hash: user.hash
          });
          
          onLogin(response.data.access_token, response.data.user);
          toast({
            title: "Success!",
            description: "Successfully registered with Telegram",
          });
          navigate("/home");
          
        } catch (error) {
          toast({
            title: "Telegram Registration Failed", 
            description: error.response?.data?.detail || "Telegram authentication failed",
            variant: "destructive"
          });
        } finally {
          setTelegramLoading(false);
        }
      };
      
    } catch (error) {
      toast({
        title: "Telegram Registration Failed",
        description: error.response?.data?.detail || "Telegram authentication failed",
        variant: "destructive"
      });
      setTelegramLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-pink-100 flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-8 animate-fadeIn">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-rose-500 mb-2">
            Join LuvHive
          </h1>
          <p className="text-gray-600">Create your anonymous profile</p>
        </div>

        <div className="glass-effect rounded-3xl p-8 shadow-xl animate-scaleIn">
          {step === 1 ? (
            <>
              <form onSubmit={handleStep1Submit} className="space-y-5">
                <div>
                  <Label htmlFor="fullName" className="text-gray-700 font-medium">Full Name</Label>
                  <Input
                    id="fullName"
                    name="fullName"
                    data-testid="fullname-input"
                    type="text"
                    placeholder="Enter your full name"
                    value={formData.fullName}
                    onChange={handleChange}
                    required
                    className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl"
                  />
                </div>

                <div>
                  <Label htmlFor="username" className="text-gray-700 font-medium">Username</Label>
                  <Input
                    id="username"
                    name="username"
                    data-testid="username-input"
                    type="text"
                    placeholder="Choose a unique username"
                    value={formData.username}
                    onChange={handleChange}
                    required
                    className={`mt-2 rounded-xl ${
                      usernameStatus === 'available' ? 'border-green-500 focus:border-green-500' :
                      usernameStatus === 'taken' ? 'border-red-500 focus:border-red-500' :
                      'border-gray-300 focus:border-pink-500'
                    }`}
                  />
                  
                  {/* Username Status Display */}
                  {usernameStatus && (
                    <div className="mt-2">
                      <p className={`text-sm flex items-center gap-2 ${
                        usernameStatus === 'available' ? 'text-green-600' :
                        usernameStatus === 'taken' ? 'text-red-600' :
                        usernameStatus === 'checking' ? 'text-blue-600' :
                        'text-gray-600'
                      }`}>
                        {usernameStatus === 'checking' && (
                          <span className="animate-spin">⏳</span>
                        )}
                        {usernameStatus === 'available' && (
                          <span>✅</span>
                        )}
                        {usernameStatus === 'taken' && (
                          <span>❌</span>
                        )}
                        {usernameMessage}
                      </p>
                      
                      {/* Username Suggestions */}
                      {usernameSuggestions.length > 0 && (
                        <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                          <p className="text-sm font-medium text-blue-800 mb-2">
                            Available suggestions:
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {usernameSuggestions.map((suggestion, index) => (
                              <button
                                key={index}
                                type="button"
                                onClick={() => selectSuggestion(suggestion)}
                                className="px-3 py-1 text-sm bg-white border border-blue-300 rounded-lg text-blue-700 hover:bg-blue-100 hover:border-blue-400 transition-colors"
                              >
                                {suggestion}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div>
                  <Label htmlFor="email" className="text-gray-700 font-medium">Email</Label>
                  <Input
                    id="email"
                    name="email"
                    data-testid="email-input"
                    type="email"
                    placeholder="Enter your email address"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className={`mt-2 rounded-xl ${
                      emailStatus === 'available' ? 'border-green-500 focus:border-green-500' :
                      emailStatus === 'taken' ? 'border-red-500 focus:border-red-500' :
                      'border-gray-300 focus:border-pink-500'
                    }`}
                  />
                  
                  {/* Email Status Display */}
                  {emailStatus && (
                    <div className="mt-2">
                      <p className={`text-sm flex items-center gap-2 ${
                        emailStatus === 'available' ? 'text-green-600' :
                        emailStatus === 'taken' ? 'text-red-600' :
                        emailStatus === 'checking' ? 'text-blue-600' :
                        'text-gray-600'
                      }`}>
                        {emailStatus === 'checking' && (
                          <span className="animate-spin">⏳</span>
                        )}
                        {emailStatus === 'available' && (
                          <span>✅</span>
                        )}
                        {emailStatus === 'taken' && (
                          <span>❌</span>
                        )}
                        {emailMessage}
                      </p>
                    </div>
                  )}
                  
                  {/* EMAIL OTP VERIFICATION */}
                  {emailStatus === 'available' && !emailVerified && (
                    <div className="mt-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <p className="text-sm font-medium text-blue-800 mb-3">
                        🔐 Email Verification Required
                      </p>
                      
                      {!emailOtpSent ? (
                        <div>
                          <p className="text-sm text-blue-700 mb-3">
                            Click below to send verification code to your email
                          </p>
                          <button
                            type="button"
                            onClick={sendEmailOtp}
                            disabled={otpLoading}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                          >
                            {otpLoading ? "Sending..." : "Send OTP to Email"}
                          </button>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          <p className="text-sm text-blue-700">
                            Enter the 6-digit code sent to your email:
                          </p>
                          <div className="flex gap-2">
                            <Input
                              type="text"
                              placeholder="Enter OTP"
                              value={emailOtp}
                              onChange={(e) => setEmailOtp(e.target.value)}
                              className="flex-1 text-center text-lg tracking-widest"
                              maxLength="6"
                            />
                            <button
                              type="button"
                              onClick={verifyEmailOtp}
                              disabled={otpLoading || !emailOtp.trim()}
                              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                            >
                              {otpLoading ? "Verifying..." : "Verify"}
                            </button>
                          </div>
                          <button
                            type="button"
                            onClick={sendEmailOtp}
                            disabled={otpLoading}
                            className="text-sm text-blue-600 hover:text-blue-800"
                          >
                            Resend OTP
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* EMAIL VERIFIED SUCCESS */}
                  {emailVerified && (
                    <div className="mt-3 p-3 bg-green-50 rounded-lg border border-green-200">
                      <p className="text-sm text-green-800 flex items-center gap-2">
                        ✅ Email verified successfully! You can now proceed to next step.
                      </p>
                    </div>
                  )}
                </div>

                <div>
                  <Label htmlFor="mobileNumber" className="text-gray-700 font-medium">
                    Mobile Number <span className="text-gray-500">(optional)</span>
                  </Label>
                  <Input
                    id="mobileNumber"
                    name="mobileNumber"
                    data-testid="mobile-input"
                    type="tel"
                    placeholder="Enter your mobile number"
                    value={formData.mobileNumber}
                    onChange={handleChange}
                    className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl"
                  />
                </div>

                <div>
                  <Label htmlFor="age" className="text-gray-700 font-medium">Age</Label>
                  <Input
                    id="age"
                    name="age"
                    data-testid="age-input"
                    type="number"
                    placeholder="Your age"
                    value={formData.age}
                    onChange={handleChange}
                    required
                    min="18"
                    className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl"
                  />
                </div>

                <div>
                  <Label htmlFor="gender" className="text-gray-700 font-medium">Gender</Label>
                  <select
                    id="gender"
                    name="gender"
                    data-testid="gender-select"
                    value={formData.gender}
                    onChange={handleChange}
                    required
                    className="mt-2 w-full border border-gray-300 rounded-xl px-4 py-2 focus:border-pink-500 focus:outline-none"
                  >
                    <option value="">Select gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <Label htmlFor="password" className="text-gray-700 font-medium">Password</Label>
                  <Input
                    id="password"
                    name="password"
                    data-testid="password-input"
                    type="password"
                    placeholder="Create a strong password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl"
                  />
                </div>

                <Button 
                  type="submit"
                  data-testid="next-step-btn"
                  disabled={!emailVerified}
                  className={`w-full py-6 rounded-xl text-lg btn-hover ${
                    emailVerified 
                      ? 'bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white' 
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {emailVerified ? 'Next Step' : 'Verify Email First'}
                </Button>
              </form>

              {/* OR Divider */}
              <div className="flex items-center my-6">
                <div className="flex-1 border-t border-gray-300"></div>
                <span className="px-4 text-gray-500 text-sm">or</span>
                <div className="flex-1 border-t border-gray-300"></div>
              </div>

              {/* Telegram Registration Button */}
              <Button
                type="button"
                onClick={handleTelegramAuth}
                disabled={telegramLoading}
                data-testid="telegram-register-btn"
                className="w-full bg-blue-500 hover:bg-blue-600 text-white py-6 text-lg rounded-xl shadow-lg flex items-center justify-center gap-2"
              >
                {telegramLoading ? (
                  "Connecting..."
                ) : (
                  <>
                    <span className="text-xl">📱</span>
                    Register with Telegram
                  </>
                )}
              </Button>
            </>
          ) : (
            <form onSubmit={handleFinalSubmit} className="space-y-5">
              <div>
                <Label htmlFor="bio" className="text-gray-700 font-medium">Bio (Optional)</Label>
                <Textarea
                  id="bio"
                  name="bio"
                  data-testid="bio-input"
                  placeholder="Tell us about yourself..."
                  value={formData.bio}
                  onChange={handleChange}
                  rows={4}
                  className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl resize-none"
                />
              </div>

              <div>
                <Label htmlFor="profileImage" className="text-gray-700 font-medium">Profile Picture (Optional)</Label>
                <Input
                  id="profileImage"
                  name="profileImage"
                  data-testid="profile-image-input"
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl"
                />
                {formData.profileImage && (
                  <div className="mt-4">
                    <img 
                      src={formData.profileImage} 
                      alt="Preview" 
                      className="w-24 h-24 rounded-full object-cover mx-auto border-4 border-pink-200"
                    />
                  </div>
                )}
              </div>

              <div className="flex gap-3">
                <Button 
                  type="button"
                  onClick={() => setStep(1)}
                  variant="outline"
                  className="flex-1 border-2 border-pink-500 text-pink-600 hover:bg-pink-50 py-6 rounded-xl"
                >
                  Back
                </Button>
                <Button 
                  type="submit"
                  data-testid="complete-registration-btn"
                  disabled={loading}
                  className="flex-1 bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white py-6 rounded-xl btn-hover"
                >
                  {loading ? "Creating..." : "Complete"}
                </Button>
              </div>
            </form>
          )}

          <div className="mt-6 text-center text-gray-600">
            <p>Already have an account? <Link to="/login" className="text-pink-600 font-semibold hover:underline">Sign In</Link></p>
          </div>
        </div>
      </div>

      {/* Success Popup */}
      <Dialog open={showSuccess} onOpenChange={setShowSuccess}>
        <DialogContent className="bg-white rounded-3xl" data-testid="success-popup">
          <DialogHeader>
            <DialogTitle className="text-3xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-rose-500">
              Registration Complete!
            </DialogTitle>
            <DialogDescription className="text-center text-xl text-gray-700 mt-4">
              Welcome To LuvHive Social
            </DialogDescription>
          </DialogHeader>
          <div className="text-center py-8">
            <div className="text-6xl mb-4">🎉</div>
            <p className="text-gray-600">Redirecting to your feed...</p>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RegisterPage;