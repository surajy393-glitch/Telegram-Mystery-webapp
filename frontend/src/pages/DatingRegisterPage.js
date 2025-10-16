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
  
  const [formData, setFormData] = useState({
    fullName: "",
    username: "",
    email: "",
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
    if (formData.fullName && formData.username && formData.email && formData.password && formData.age && formData.gender) {
      if (parseInt(formData.age) < 18) {
        toast({
          title: "Age Requirement",
          description: "You must be 18 or older to register",
          variant: "destructive"
        });
        return;
      }
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
      formDataToSend.append("email", formData.email);
      formDataToSend.append("password", formData.password);
      formDataToSend.append("age", parseInt(formData.age));
      formDataToSend.append("gender", formData.gender);
      formDataToSend.append("city", formData.city);
      formDataToSend.append("interests", formData.interests.join(", "));

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
                    className="mt-2 bg-white bg-opacity-20 text-white placeholder:text-white placeholder:text-opacity-60 border-white border-opacity-30 focus:border-pink-300 rounded-xl"
                  />
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