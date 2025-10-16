import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DatingRegisterPage = ({ onLogin }) => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  // OTP and verification states
  const [usernameStatus, setUsernameStatus] = useState(null);
  const [usernameSuggestions, setUsernameSuggestions] = useState([]);
  const [usernameMessage, setUsernameMessage] = useState("");
  const [emailStatus, setEmailStatus] = useState(null);
  const [emailMessage, setEmailMessage] = useState("");
  const [emailOtpSent, setEmailOtpSent] = useState(false);
  const [emailOtp, setEmailOtp] = useState("");
  const [emailVerified, setEmailVerified] = useState(false);
  const [otpLoading, setOtpLoading] = useState(false);
  const [mobileOtpSent, setMobileOtpSent] = useState(false);
  const [mobileOtp, setMobileOtp] = useState("");
  const [mobileVerified, setMobileVerified] = useState(false);
  const [mobileOtpLoading, setMobileOtpLoading] = useState(false);
  const [mobileStatus, setMobileStatus] = useState(null);
  const [mobileMessage, setMobileMessage] = useState("");
  
  const [formData, setFormData] = useState({
    fullName: "",
    username: "",
    email: "",
    mobileNumber: "",
    password: "",
    age: "",
    gender: "",
    city: "",
    interests: []
  });

  const interestOptions = [
    "Travel", "Food", "Music", "Movies", "Sports", "Reading",
    "Gaming", "Fitness", "Art", "Photography", "Dancing", "Cooking"
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Check username availability
    if (name === 'username') {
      checkUsernameAvailability(value);
    }
    
    // Check email availability
    if (name === 'email') {
      checkEmailAvailability(value);
    }
    
    // Check mobile availability
    if (name === 'mobileNumber') {
      checkMobileAvailability(value);
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
        setUsernameSuggestions(data.suggestions || []);
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

  const checkMobileAvailability = async (mobile) => {
    if (!mobile || mobile.length < 10) {
      setMobileStatus(null);
      setMobileMessage("");
      return;
    }

    setMobileStatus('checking');
    setMobileMessage("Checking mobile number...");
    
    try {
      const response = await axios.get(`${API}/auth/check-mobile/${encodeURIComponent(mobile)}`);
      const data = response.data;
      
      if (data.available) {
        setMobileStatus('available');
        setMobileMessage(data.message);
      } else {
        setMobileStatus('taken');
        setMobileMessage(data.message);
      }
    } catch (error) {
      setMobileStatus('error');
      setMobileMessage("Error checking mobile number");
    }
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

  const sendMobileOtp = async () => {
    if (!formData.mobileNumber || !formData.mobileNumber.trim()) {
      toast({
        title: "Error",
        description: "Please enter your mobile number first",
        variant: "destructive"
      });
      return;
    }

    if (mobileStatus === 'taken') {
      toast({
        title: "Error",
        description: "This mobile number is already registered",
        variant: "destructive"
      });
      return;
    }

    if (mobileStatus !== 'available') {
      toast({
        title: "Error",
        description: "Please wait for mobile number validation",
        variant: "destructive"
      });
      return;
    }

    setMobileOtpLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/send-mobile-otp`, {
        mobileNumber: formData.mobileNumber
      });
      
      if (response.data.otpSent) {
        setMobileOtpSent(true);
        toast({
          title: "OTP Sent! 📱",
          description: "Check your mobile for the verification code",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to send mobile OTP",
        variant: "destructive"
      });
    } finally {
      setMobileOtpLoading(false);
    }
  };

  const verifyMobileOtp = async () => {
    if (!mobileOtp.trim()) {
      toast({
        title: "Error",
        description: "Please enter the mobile OTP",
        variant: "destructive"
      });
      return;
    }

    setMobileOtpLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/verify-mobile-otp`, {
        mobileNumber: formData.mobileNumber,
        otp: mobileOtp.trim()
      });
      
      if (response.data.verified) {
        setMobileVerified(true);
        toast({
          title: "Mobile Verified! ✅",
          description: "Mobile number verified successfully",
        });
      }
    } catch (error) {
      toast({
        title: "Invalid OTP",
        description: error.response?.data?.detail || "Mobile OTP verification failed",
        variant: "destructive"
      });
    } finally {
      setMobileOtpLoading(false);
    }
  };

  const toggleInterest = (interest) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const handleStep1Submit = (e) => {
    e.preventDefault();
    
    // REQUIRE either email OR mobile verification before proceeding
    if (!emailVerified && !mobileVerified) {
      toast({
        title: "Verification Required",
        description: "Please verify either your email or mobile number before proceeding",
        variant: "destructive"
      });
      return;
    }
    
    if (formData.fullName && formData.username && (formData.email || mobileVerified) && formData.age && formData.gender && formData.password) {
      setStep(2);
    }
  };

  const handleFinalSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.city) {
      toast({
        title: "City Required",
        description: "Please enter your city",
        variant: "destructive"
      });
      return;
    }

    if (formData.interests.length === 0) {
      toast({
        title: "Interests Required",
        description: "Please select at least one interest",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);

    try {
      // Register user in web app (MongoDB) AND bot database (PostgreSQL)
      const formDataToSend = new FormData();
      formDataToSend.append("fullName", formData.fullName);
      formDataToSend.append("username", formData.username);
      formDataToSend.append("email", formData.email || "");
      formDataToSend.append("mobileNumber", formData.mobileNumber || "");
      formDataToSend.append("password", formData.password);
      formDataToSend.append("age", parseInt(formData.age));
      formDataToSend.append("gender", formData.gender);
      formDataToSend.append("city", formData.city);
      formDataToSend.append("interests", formData.interests.join(", "));
      formDataToSend.append("emailVerified", emailVerified);
      formDataToSend.append("mobileVerified", mobileVerified);

      const response = await axios.post(`${API}/auth/register-for-mystery`, formDataToSend, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });

      const token = response.data.access_token;
      const userData = response.data.user;

      // Save token and user data
      onLogin(token, userData);

      toast({
        title: "Registration Successful! 🎉",
        description: "Welcome to Mystery Match!",
      });

      // Navigate to Mystery Match home
      setTimeout(() => {
        navigate("/mystery");
      }, 500);
      
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-500 via-pink-500 to-red-500 flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-8 animate-fadeIn">
          <h1 className="text-5xl font-bold text-white mb-2">
            🎭 Mystery Match
          </h1>
          <p className="text-white text-opacity-90">Create your anonymous dating profile</p>
        </div>

        <div className="glass-effect rounded-3xl p-8 shadow-xl">
          {/* Progress Indicator */}
          <div className="flex items-center justify-center mb-6">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-pink-500' : 'bg-gray-300'} text-white font-bold`}>
              1
            </div>
            <div className={`w-16 h-1 ${step >= 2 ? 'bg-pink-500' : 'bg-gray-300'}`}></div>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-pink-500' : 'bg-gray-300'} text-white font-bold`}>
              2
            </div>
          </div>

          {step === 1 ? (
            <>
              <h2 className="text-2xl font-bold text-white mb-6 text-center">Basic Info</h2>
              <form onSubmit={handleStep1Submit} className="space-y-4">
                <div>
                  <Label htmlFor="fullName" className="text-white font-medium">Full Name</Label>
                  <Input
                    id="fullName"
                    name="fullName"
                    type="text"
                    placeholder="Enter your full name"
                    value={formData.fullName}
                    onChange={handleChange}
                    required
                    className="mt-2 bg-white bg-opacity-20 text-white placeholder:text-white placeholder:text-opacity-60 border-white border-opacity-30 focus:border-pink-300 rounded-xl"
                  />
                </div>

                <div>
                  <Label htmlFor="username" className="text-white font-medium">Username</Label>
                  <Input
                    id="username"
                    name="username"
                    type="text"
                    placeholder="Choose a unique username"
                    value={formData.username}
                    onChange={handleChange}
                    required
                    className={`mt-2 bg-white bg-opacity-20 text-white placeholder:text-white placeholder:text-opacity-60 rounded-xl ${
                      usernameStatus === 'available' ? 'border-green-400 border-2' :
                      usernameStatus === 'taken' ? 'border-red-400 border-2' :
                      'border-white border-opacity-30'
                    }`}
                  />
                  
                  {/* Username Status Display */}
                  {usernameStatus && (
                    <div className="mt-2">
                      <p className={`text-sm flex items-center gap-2 ${
                        usernameStatus === 'available' ? 'text-green-300' :
                        usernameStatus === 'taken' ? 'text-red-300' :
                        usernameStatus === 'checking' ? 'text-blue-300' :
                        'text-white text-opacity-70'
                      }`}>
                        {usernameStatus === 'checking' && <span className="animate-spin">⏳</span>}
                        {usernameStatus === 'available' && <span>✅</span>}
                        {usernameStatus === 'taken' && <span>❌</span>}
                        {usernameMessage}
                      </p>
                      
                      {/* Username Suggestions */}
                      {usernameSuggestions.length > 0 && (
                        <div className="mt-3 p-3 bg-blue-500 bg-opacity-20 rounded-lg border border-blue-300 border-opacity-30">
                          <p className="text-sm font-medium text-blue-200 mb-2">
                            Available suggestions:
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {usernameSuggestions.map((suggestion, index) => (
                              <button
                                key={index}
                                type="button"
                                onClick={() => selectSuggestion(suggestion)}
                                className="px-3 py-1 text-sm bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg text-white hover:bg-opacity-30 transition-colors"
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
                  <Label htmlFor="email" className="text-white font-medium">Email</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="your@email.com"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="mt-2 bg-white bg-opacity-20 text-white placeholder:text-white placeholder:text-opacity-60 border-white border-opacity-30 focus:border-pink-300 rounded-xl"
                  />
                </div>

                <div>
                  <Label htmlFor="password" className="text-white font-medium">Password</Label>
                  <div className="relative mt-2">
                    <Input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Create a strong password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      className="bg-white bg-opacity-20 text-white placeholder:text-white placeholder:text-opacity-60 border-white border-opacity-30 focus:border-pink-300 rounded-xl pr-12"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white hover:text-pink-200 focus:outline-none"
                    >
                      {showPassword ? (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L8.464 8.464M14.12 14.12l1.414 1.414M9.878 9.878l-4.414-4.414m14.071 14.071L20.95 20.95M9.878 9.878l4.242 4.242" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="age" className="text-white font-medium">Age</Label>
                    <Input
                      id="age"
                      name="age"
                      type="number"
                      placeholder="18+"
                      value={formData.age}
                      onChange={handleChange}
                      required
                      min="18"
                      className="mt-2 bg-white bg-opacity-20 text-white placeholder:text-white placeholder:text-opacity-60 border-white border-opacity-30 focus:border-pink-300 rounded-xl"
                    />
                  </div>

                  <div>
                    <Label htmlFor="gender" className="text-white font-medium">Gender</Label>
                    <select
                      id="gender"
                      name="gender"
                      value={formData.gender}
                      onChange={handleChange}
                      required
                      className="mt-2 w-full bg-white bg-opacity-20 text-white border-white border-opacity-30 rounded-xl px-4 py-2 focus:border-pink-300 focus:outline-none"
                    >
                      <option value="" className="text-gray-800">Select</option>
                      <option value="Male" className="text-gray-800">Male</option>
                      <option value="Female" className="text-gray-800">Female</option>
                      <option value="Other" className="text-gray-800">Other</option>
                    </select>
                  </div>
                </div>

                <Button 
                  type="submit"
                  className="w-full bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white py-6 rounded-xl text-lg font-bold shadow-2xl"
                >
                  Next Step →
                </Button>
              </form>
            </>
          ) : (
            <>
              <h2 className="text-2xl font-bold text-white mb-6 text-center">Dating Profile</h2>
              <form onSubmit={handleFinalSubmit} className="space-y-5">
                <div>
                  <Label htmlFor="city" className="text-white font-medium">City</Label>
                  <Input
                    id="city"
                    name="city"
                    type="text"
                    placeholder="Enter your city"
                    value={formData.city}
                    onChange={handleChange}
                    required
                    className="mt-2 bg-white bg-opacity-20 text-white placeholder:text-white placeholder:text-opacity-60 border-white border-opacity-30 focus:border-pink-300 rounded-xl"
                  />
                </div>

                <div>
                  <Label className="text-white font-medium mb-3 block">Interests (Select at least 1)</Label>
                  <div className="grid grid-cols-3 gap-2">
                    {interestOptions.map(interest => (
                      <button
                        key={interest}
                        type="button"
                        onClick={() => toggleInterest(interest)}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition ${
                          formData.interests.includes(interest)
                            ? 'bg-pink-500 text-white'
                            : 'bg-white bg-opacity-20 text-white border border-white border-opacity-30 hover:bg-opacity-30'
                        }`}
                      >
                        {interest}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="bg-white bg-opacity-10 rounded-xl p-4 text-white text-sm">
                  <div className="flex items-start space-x-2">
                    <span className="text-xl">🎭</span>
                    <div>
                      <p className="font-semibold mb-1">Mystery Match Privacy</p>
                      <p className="text-white text-opacity-80">Your profile stays hidden until you chat and unlock it progressively. Perfect for privacy-conscious dating!</p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button 
                    type="button"
                    onClick={() => setStep(1)}
                    className="flex-1 bg-white bg-opacity-20 hover:bg-opacity-30 text-white border border-white border-opacity-30 py-6 rounded-xl"
                  >
                    ← Back
                  </Button>
                  <Button 
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white py-6 rounded-xl text-lg font-bold shadow-2xl"
                  >
                    {loading ? "Creating..." : "Complete 🎉"}
                  </Button>
                </div>
              </form>
            </>
          )}

          <div className="mt-6 text-center text-white text-opacity-90">
            <p>Already have an account? <Link to="/login" className="text-pink-200 font-semibold hover:underline">Sign In</Link></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DatingRegisterPage;