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
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
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

          // Send real Telegram data with hash for verification
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
                    className="mt-2 border-gray-300 focus:border-pink-500 rounded-xl"
                  />
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
                  className="w-full bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white py-6 rounded-xl text-lg btn-hover"
                >
                  Next Step
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