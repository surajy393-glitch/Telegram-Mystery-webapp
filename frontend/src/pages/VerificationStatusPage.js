import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowLeft, CheckCircle2, XCircle, Shield } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

const VerificationStatusPage = ({ user }) => {
  const navigate = useNavigate();
  const [verificationData, setVerificationData] = useState(null);
  const [loading, setLoading] = useState(true);

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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-white">
        <div className="text-2xl text-blue-600">Loading...</div>
      </div>
    );
  }

  const criteria = [
    {
      key: 'accountAge',
      label: 'Account Age',
      requirement: '45+ days old',
      met: verificationData?.criteria?.accountAge || false,
      value: verificationData?.currentValues?.accountAgeDays || 0,
      progress: `${verificationData?.currentValues?.accountAgeDays || 0} days`
    },
    {
      key: 'emailVerified',
      label: 'Email Verified',
      requirement: 'Email address verified',
      met: verificationData?.criteria?.emailVerified || false,
      value: verificationData?.currentValues?.emailVerified ? 1 : 0,
      progress: verificationData?.currentValues?.emailVerified ? 'Verified' : 'Not verified'
    },
    {
      key: 'phoneVerified',
      label: 'Phone Verified',
      requirement: 'Phone number verified',
      met: verificationData?.criteria?.phoneVerified || false,
      value: verificationData?.currentValues?.phoneVerified ? 1 : 0,
      progress: verificationData?.currentValues?.phoneVerified ? 'Verified' : 'Not verified'
    },
    {
      key: 'postsCount',
      label: 'Posts',
      requirement: '20+ posts',
      met: verificationData?.criteria?.postsCount || false,
      value: verificationData?.currentValues?.postsCount || 0,
      progress: `${verificationData?.currentValues?.postsCount || 0}/20 posts`
    },
    {
      key: 'followersCount',
      label: 'Followers',
      requirement: '100+ followers',
      met: verificationData?.criteria?.followersCount || false,
      value: verificationData?.currentValues?.followersCount || 0,
      progress: `${verificationData?.currentValues?.followersCount || 0}/100 followers`
    },
    {
      key: 'noViolations',
      label: 'No Violations',
      requirement: 'Zero community violations',
      met: verificationData?.criteria?.noViolations || false,
      value: verificationData?.currentValues?.violationsCount === 0 ? 1 : 0,
      progress: `${verificationData?.currentValues?.violationsCount || 0} violations`
    },
    {
      key: 'profileComplete',
      label: 'Complete Profile',
      requirement: 'All profile fields filled',
      met: verificationData?.criteria?.profileComplete || false,
      value: verificationData?.currentValues?.profileComplete ? 1 : 0,
      progress: verificationData?.currentValues?.profileComplete ? 'Complete' : 'Incomplete'
    },
    {
      key: 'personalityQuestions',
      label: 'Personality Quiz',
      requirement: 'Answered personality questions',
      met: verificationData?.criteria?.personalityQuestions || false,
      value: verificationData?.currentValues?.personalityQuestions ? 1 : 0,
      progress: verificationData?.currentValues?.personalityQuestions ? 'Completed' : 'Not completed'
    },
    {
      key: 'profileViews',
      label: 'Profile Views',
      requirement: '1000+ profile views',
      met: verificationData?.criteria?.profileViews || false,
      value: verificationData?.currentValues?.profileViews || 0,
      progress: `${verificationData?.currentValues?.profileViews || 0}/1000 views`
    },
    {
      key: 'avgStoryViews',
      label: 'Story Engagement',
      requirement: '70+ avg story views',
      met: verificationData?.criteria?.avgStoryViews || false,
      value: verificationData?.currentValues?.avgStoryViews || 0,
      progress: `${verificationData?.currentValues?.avgStoryViews || 0}/70 avg views`
    },
    {
      key: 'totalLikes',
      label: 'Total Likes',
      requirement: '1000+ total likes',
      met: verificationData?.criteria?.totalLikes || false,
      value: verificationData?.currentValues?.totalLikes || 0,
      progress: `${verificationData?.currentValues?.totalLikes || 0}/1000 likes`
    }
  ];

  const metCriteria = criteria.filter(c => c.met).length;
  const totalCriteria = criteria.length;
  // If user is verified, show 100% regardless of individual criteria
  const overallProgress = verificationData?.isVerified ? 100 : Math.round((metCriteria / totalCriteria) * 100);

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

        {/* Show criteria only if not verified yet */}
        {!verificationData?.isVerified && (
        <div className="glass-effect rounded-3xl p-6 shadow-xl">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Verification Criteria</h3>
          <div className="space-y-3">
            {criteria.map((criterion) => (
              <div 
                key={criterion.key}
                className={`p-4 rounded-xl border-2 transition-all ${
                  criterion.met 
                    ? 'bg-green-50 border-green-300' 
                    : 'bg-gray-50 border-gray-200'
                }`}
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
            ))}
          </div>
        </div>
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
    </div>
  );
};

export default VerificationStatusPage;
