import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ArrowLeft, CheckCircle2, XCircle, Shield } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

const VerificationStatusPage = ({ user }) => {
  const navigate = useNavigate();
  const [verificationData, setVerificationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showVerifyDialog, setShowVerifyDialog] = useState(false);
  const [verificationType, setVerificationType] = useState(''); // 'email' or 'phone'
  const [verificationStep, setVerificationStep] = useState('send'); // 'send' or 'verify'
  const [otpCode, setOtpCode] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [email, setEmail] = useState('');
  const [verifying, setVerifying] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' or 'error'

  useEffect(() => {
    fetchVerificationStatus();
  }, []);

  const fetchVerificationStatus = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API}/verification/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setVerificationData(response.data);
    } catch (error) {
      console.error("Error fetching verification status:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleVerificationClick = (type) => {
    setVerificationType(type);
    setVerificationStep('send');
    setOtpCode('');
    setMessage('');
    setShowVerifyDialog(true);
  };

  const sendVerificationCode = async () => {
    setVerifying(true);
    setMessage('');
    try {
      const token = localStorage.getItem("token");
      
      if (verificationType === 'email') {
        const response = await axios.post(`${API}/auth/send-email-verification`, 
          { email },
          { headers: { Authorization: `Bearer ${token}` }}
        );
        // For email, show debug code since we're not sending real emails yet
        setMessage(`Code sent! For testing: ${response.data.debug_code}`);
        setMessageType('success');
      } else {
        await axios.post(`${API}/auth/send-phone-verification`, 
          { phone: phoneNumber },
          { headers: { Authorization: `Bearer ${token}` }}
        );
        setMessage('Verification code sent to your phone via SMS!');
        setMessageType('success');
      }
      setVerificationStep('verify');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Failed to send verification code');
      setMessageType('error');
    } finally {
      setVerifying(false);
    }
  };

  const verifyCode = async () => {
    setVerifying(true);
    setMessage('');
    try {
      const token = localStorage.getItem("token");
      
      if (verificationType === 'email') {
        await axios.post(`${API}/auth/verify-email-code`, 
          { code: otpCode },
          { headers: { Authorization: `Bearer ${token}` }}
        );
        setMessage('Email verified successfully!');
      } else {
        await axios.post(`${API}/auth/verify-phone-code`, 
          { code: otpCode },
          { headers: { Authorization: `Bearer ${token}` }}
        );
        setMessage('Phone verified successfully!');
      }
      setMessageType('success');
      
      // Refresh verification status
      setTimeout(() => {
        setShowVerifyDialog(false);
        fetchVerificationStatus();
      }, 1500);
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Invalid verification code');
      setMessageType('error');
    } finally {
      setVerifying(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-white">
        <div className="text-2xl text-blue-600">Loading...</div>
      </div>
    );
  }

  // Group criteria by category
  const identitySecurityCriteria = [
    {
      key: 'emailVerified',
      label: 'Email Verified',
      requirement: 'Verify your email address',
      met: verificationData?.criteria?.emailVerified || false,
      progress: verificationData?.currentValues?.emailVerified ? 'Verified' : 'Not verified'
    },
    {
      key: 'phoneVerified',
      label: 'Phone Verified',
      requirement: 'Verify your phone number',
      met: verificationData?.criteria?.phoneVerified || false,
      progress: verificationData?.currentValues?.phoneVerified ? 'Verified' : 'Not verified'
    }
  ];

  const profileCompletenessCriteria = [
    {
      key: 'profileComplete',
      label: 'Complete Profile',
      requirement: 'Fill all profile fields',
      met: verificationData?.criteria?.profileComplete || false,
      progress: verificationData?.currentValues?.profileComplete ? 'Complete' : 'Incomplete'
    },
    {
      key: 'personalityQuestions',
      label: 'Personality Quiz',
      requirement: 'Complete personality questions',
      met: true,
      progress: 'Completed'
    }
  ];

  const tenureBehaviourCriteria = [
    {
      key: 'accountAge',
      label: 'Account Age',
      requirement: '45+ days old',
      met: verificationData?.criteria?.accountAge || false,
      progress: `${verificationData?.currentValues?.accountAgeDays || 0} days`
    },
    {
      key: 'noViolations',
      label: 'No Violations',
      requirement: 'Zero community violations',
      met: verificationData?.criteria?.noViolations || false,
      progress: `${verificationData?.currentValues?.violationsCount || 0} violations`
    }
  ];

  // Pathways
  const pathways = [
    {
      id: 'highEngagement',
      name: '🔥 High Engagement Pathway',
      description: 'For active community members with strong presence',
      met: verificationData?.pathways?.highEngagement || false,
      requirements: [
        { label: '20+ Posts', met: verificationData?.criteria?.postsCount, value: `${verificationData?.currentValues?.postsCount || 0}/20` },
        { label: '100+ Followers', met: verificationData?.criteria?.followersCount, value: `${verificationData?.currentValues?.followersCount || 0}/100` },
        { label: '1000+ Total Likes', met: verificationData?.criteria?.totalLikes, value: `${verificationData?.currentValues?.totalLikes || 0}/1000` },
        { label: '70+ Avg Story Views', met: verificationData?.criteria?.avgStoryViews, value: `${verificationData?.currentValues?.avgStoryViews || 0}/70` },
        { label: '1000+ Profile Views', met: verificationData?.criteria?.profileViews, value: `${verificationData?.currentValues?.profileViews || 0}/1000` }
      ]
    },
    {
      id: 'moderateEngagement',
      name: '⭐ Moderate Engagement Pathway',
      description: 'For consistent users with longer account history',
      met: verificationData?.pathways?.moderateEngagement || false,
      requirements: [
        { label: '10+ Posts', met: verificationData?.currentValues?.moderateEngagementPosts, value: `${verificationData?.currentValues?.postsCount || 0}/10` },
        { label: '50+ Followers', met: verificationData?.currentValues?.moderateEngagementFollowers, value: `${verificationData?.currentValues?.followersCount || 0}/50` },
        { label: '90+ Days Old', met: verificationData?.currentValues?.moderateEngagementTenure, value: `${verificationData?.currentValues?.accountAgeDays || 0}/90` },
        { label: '500+ Likes OR 40+ Avg Story Views', met: verificationData?.currentValues?.moderateEngagementLikes, value: 'Check engagement' }
      ]
    },
    {
      id: 'communityContribution',
      name: '🏆 Community Contribution',
      description: 'For moderators, event organizers, and active contributors',
      met: verificationData?.pathways?.communityContribution || false,
      requirements: [
        { label: 'Coming Soon', met: false, value: 'Apply via moderator program' }
      ]
    },
    {
      id: 'crossPlatform',
      name: '🔗 Cross-Platform Verified',
      description: 'Already verified on Instagram, Twitter, or LinkedIn',
      met: verificationData?.pathways?.crossPlatformVerified || false,
      requirements: [
        { label: 'Coming Soon', met: false, value: 'Link verified account' }
      ]
    }
  ];

  const allGroups = [
    { title: '1. Identity & Security', criteria: identitySecurityCriteria, required: true },
    { title: '2. Profile Completeness', criteria: profileCompletenessCriteria, required: true },
    { title: '3. Tenure & Behaviour', criteria: tenureBehaviourCriteria, required: true }
  ];

  const basicRequirementsMet = identitySecurityCriteria.every(c => c.met) && 
                                profileCompletenessCriteria.every(c => c.met) &&
                                tenureBehaviourCriteria.every(c => c.met);

  const anyPathwayMet = pathways.some(p => p.met);

  // Calculate overall progress
  const basicCount = [...identitySecurityCriteria, ...profileCompletenessCriteria, ...tenureBehaviourCriteria].filter(c => c.met).length;
  const basicTotal = identitySecurityCriteria.length + profileCompletenessCriteria.length + tenureBehaviourCriteria.length;
  const overallProgress = verificationData?.isVerified ? 100 : Math.round((basicCount / basicTotal) * 100);

  // Flatten all criteria for display
  const criteria = [...identitySecurityCriteria, ...profileCompletenessCriteria, ...tenureBehaviourCriteria];
  const metCriteria = criteria.filter(c => c.met).length;
  const totalCriteria = criteria.length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100">
      {/* Header */}
      <header className="glass-effect border-b border-blue-100 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center">
          <Button 
            variant="ghost" 
            className="hover:bg-blue-50 mr-3"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft className="w-5 h-5 text-blue-600" />
          </Button>
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">
            LuvHive Verified
          </h1>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-2xl">
        {/* Verification Status Card */}
        <div className={`glass-effect rounded-3xl p-8 mb-6 shadow-xl animate-fadeIn ${verificationData?.isVerified ? 'bg-gradient-to-br from-green-50 to-blue-50' : ''}`}>
          <div className="text-center mb-6">
            <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full mb-4 ${verificationData?.isVerified ? 'bg-gradient-to-br from-green-500 to-blue-500' : 'bg-gradient-to-br from-blue-500 to-cyan-500'}`}>
              {verificationData?.isVerified ? (
                <CheckCircle2 className="w-12 h-12 text-white" />
              ) : (
                <Shield className="w-12 h-12 text-white" />
              )}
            </div>
            <h2 className="text-3xl font-bold text-gray-800 mb-2">
              {verificationData?.isVerified ? '🎉 You\'re Verified!' : 'Verification Progress'}
            </h2>
            <p className="text-gray-600">
              {verificationData?.isVerified 
                ? 'Your account has been verified with the blue checkmark ☑️'
                : `${metCriteria} of ${totalCriteria} criteria met`}
            </p>
          </div>

          {/* Progress Bar */}
          <div className="bg-gray-200 rounded-full h-4 overflow-hidden mb-2">
            <div 
              className={`h-full transition-all duration-500 ease-out ${verificationData?.isVerified ? 'bg-gradient-to-r from-green-500 to-blue-500' : 'bg-gradient-to-r from-blue-500 to-cyan-500'}`}
              style={{ width: `${overallProgress}%` }}
            />
          </div>
          <p className="text-right text-sm text-gray-600 font-semibold">{overallProgress}% Complete</p>
        </div>

        {/* Show grouped criteria if not verified yet */}
        {!verificationData?.isVerified && (
        <>
          {/* Basic Requirements */}
          <div className="glass-effect rounded-3xl p-6 shadow-xl mb-6">
            <h3 className="text-xl font-bold text-gray-800 mb-2">Basic Requirements</h3>
            <p className="text-sm text-gray-600 mb-4">Complete all sections below to qualify for verification</p>
            
            {allGroups.map((group, groupIdx) => (
              <div key={groupIdx} className="mb-6 last:mb-0">
                <h4 className="text-lg font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  {group.title}
                  {group.criteria.every(c => c.met) && <CheckCircle2 className="w-5 h-5 text-green-600" />}
                </h4>
                <div className="space-y-3">
                  {group.criteria.map((criterion) => {
                    const isVerifiable = (criterion.key === 'emailVerified' || criterion.key === 'phoneVerified') && !criterion.met;
                    
                    return (
                      <div 
                        key={criterion.key}
                        className={`p-4 rounded-xl border-2 transition-all ${
                          criterion.met 
                            ? 'bg-green-50 border-green-300' 
                            : isVerifiable 
                            ? 'bg-blue-50 border-blue-300 cursor-pointer hover:border-blue-400 hover:shadow-md' 
                            : 'bg-gray-50 border-gray-200'
                        }`}
                        onClick={() => isVerifiable && handleVerificationClick(criterion.key === 'emailVerified' ? 'email' : 'phone')}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              {criterion.met ? (
                                <CheckCircle2 className="w-5 h-5 text-green-600" />
                              ) : (
                                <XCircle className="w-5 h-5 text-gray-400" />
                              )}
                              <h4 className="font-semibold text-gray-800">{criterion.label}</h4>
                              {isVerifiable && (
                                <span className="text-xs bg-blue-500 text-white px-2 py-1 rounded-full ml-2">
                                  Click to Verify
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 ml-7">{criterion.requirement}</p>
                          </div>
                          <div className="text-right">
                            <p className={`text-sm font-medium ${
                              criterion.met ? 'text-green-600' : 'text-gray-500'
                            }`}>
                              {criterion.progress}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* Verification Pathways */}
          <div className="glass-effect rounded-3xl p-6 shadow-xl mb-6">
            <h3 className="text-xl font-bold text-gray-800 mb-2">Choose Your Pathway to Verification</h3>
            <p className="text-sm text-gray-600 mb-4">
              {basicRequirementsMet 
                ? "✅ Basic requirements met! Complete ANY ONE pathway below to qualify for verification."
                : "⚠️ Complete basic requirements first, then choose one pathway to pursue."}
            </p>

            <div className="space-y-4">
              {pathways.map((pathway) => (
                <div 
                  key={pathway.id}
                  className={`p-5 rounded-xl border-2 transition-all ${
                    pathway.met 
                      ? 'bg-gradient-to-br from-green-50 to-green-100 border-green-400 shadow-lg' 
                      : 'bg-white border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="text-lg font-bold text-gray-800 mb-1 flex items-center gap-2">
                        {pathway.name}
                        {pathway.met && <CheckCircle2 className="w-6 h-6 text-green-600" />}
                      </h4>
                      <p className="text-sm text-gray-600">{pathway.description}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2 mt-3">
                    {pathway.requirements.map((req, idx) => (
                      <div key={idx} className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          {req.met ? (
                            <CheckCircle2 className="w-4 h-4 text-green-600" />
                          ) : (
                            <XCircle className="w-4 h-4 text-gray-400" />
                          )}
                          <span className={req.met ? 'text-green-700 font-medium' : 'text-gray-600'}>
                            {req.label}
                          </span>
                        </div>
                        <span className="text-xs text-gray-500">{req.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
        )}

        {/* Success message for verified users */}
        {verificationData?.isVerified && (
        <div className="glass-effect rounded-3xl p-6 shadow-xl bg-gradient-to-br from-green-50 to-blue-50">
          <h3 className="text-xl font-bold text-gray-800 mb-3">🎉 Congratulations!</h3>
          <p className="text-gray-700 leading-relaxed mb-4">
            You are now a verified member of LuvHive! Your blue checkmark badge appears next to your username across the platform, helping others know your account is authentic.
          </p>
          <div className="bg-white bg-opacity-60 rounded-xl p-4">
            <h4 className="font-semibold text-gray-800 mb-2">✨ Verified Badge Benefits:</h4>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>• Blue checkmark ☑️ on your profile</li>
              <li>• Badge appears on all your posts</li>
              <li>• Badge visible in story viewer</li>
              <li>• Enhanced credibility and trust</li>
              <li>• Stand out in search results</li>
            </ul>
          </div>
        </div>
        )}

        {/* Info Box - only for non-verified */}
        {!verificationData?.isVerified && (
        <div className="glass-effect rounded-3xl p-6 mt-6 shadow-xl bg-blue-50">
          <h3 className="text-lg font-bold text-gray-800 mb-2">💡 About Verification</h3>
          <p className="text-sm text-gray-600 leading-relaxed">
            The blue verified badge helps people know that notable accounts are authentic. 
            To get verified, you need to meet all the criteria listed above. Keep engaging 
            with the community, creating quality content, and building your presence on LuvHive!
          </p>
        </div>
        )}
      </div>

      {/* Verification Dialog */}
      <Dialog open={showVerifyDialog} onOpenChange={setShowVerifyDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>
              Verify Your {verificationType === 'email' ? 'Email' : 'Phone Number'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            {verificationStep === 'send' ? (
              <>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    {verificationType === 'email' ? 'Email Address' : 'Phone Number'}
                  </label>
                  {verificationType === 'email' ? (
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  ) : (
                    <input
                      type="tel"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      placeholder="Enter your phone number"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  )}
                </div>
                
                <Button 
                  onClick={sendVerificationCode}
                  disabled={verifying || (verificationType === 'email' ? !email : !phoneNumber)}
                  className="w-full bg-blue-500 hover:bg-blue-600 text-white"
                >
                  {verifying ? 'Sending...' : 'Send Verification Code'}
                </Button>
              </>
            ) : (
              <>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    Enter Verification Code
                  </label>
                  <input
                    type="text"
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value)}
                    placeholder="Enter 6-digit code"
                    maxLength={6}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center text-2xl tracking-widest"
                  />
                </div>
                
                <Button 
                  onClick={verifyCode}
                  disabled={verifying || otpCode.length !== 6}
                  className="w-full bg-green-500 hover:bg-green-600 text-white"
                >
                  {verifying ? 'Verifying...' : 'Verify Code'}
                </Button>
                
                <button
                  onClick={() => setVerificationStep('send')}
                  className="w-full text-sm text-blue-600 hover:underline"
                >
                  Didn't receive code? Send again
                </button>
              </>
            )}
            
            {message && (
              <div className={`p-3 rounded-lg ${
                messageType === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
              }`}>
                {message}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default VerificationStatusPage;
