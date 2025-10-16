import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-500 via-pink-500 to-red-500">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center animate-fadeIn">
          <div className="text-7xl mb-6">🎭</div>
          <h1 className="text-6xl md:text-7xl font-bold text-white mb-6">
            LuvHive Mystery Match
          </h1>
          <p className="text-xl md:text-2xl text-white text-opacity-90 mb-4 max-w-3xl mx-auto">
            Safe, Anonymous, and Culturally Respectful Dating
          </p>
          <p className="text-lg text-white text-opacity-80 mb-12 max-w-2xl mx-auto">
            Progressive profile reveals. No awkward screenshots. Perfect for privacy-conscious Indians.
          </p>
          
          <div className="flex gap-4 justify-center flex-wrap">
            <Link to="/register">
              <Button 
                data-testid="get-started-btn"
                className="bg-white text-purple-600 hover:bg-opacity-90 px-8 py-6 text-lg rounded-full font-bold shadow-2xl"
              >
                Start Mystery Matching 🎲
              </Button>
            </Link>
            <Link to="/login">
              <Button 
                data-testid="login-btn"
                className="bg-white bg-opacity-20 border-2 border-white text-white hover:bg-opacity-30 px-8 py-6 text-lg rounded-full font-bold"
              >
                Sign In
              </Button>
            </Link>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-24 grid md:grid-cols-3 gap-8 animate-slideIn">
          <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-3xl p-8 text-center border border-white border-opacity-20 hover:bg-opacity-20 transition-all duration-300">
            <div className="text-5xl mb-4">🎭</div>
            <h3 className="text-2xl font-bold text-white mb-3">Progressive Unlock</h3>
            <p className="text-white text-opacity-80">
              Profiles reveal gradually as you chat. No instant photo sharing!
            </p>
          </div>

          <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-3xl p-8 text-center border border-white border-opacity-20 hover:bg-opacity-20 transition-all duration-300">
            <div className="text-5xl mb-4">🔐</div>
            <h3 className="text-2xl font-bold text-white mb-3">Privacy First</h3>
            <p className="text-white text-opacity-80">
              No screenshots or downloads. Messages disappear after 48 hours.
            </p>
          </div>

          <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-3xl p-8 text-center border border-white border-opacity-20 hover:bg-opacity-20 transition-all duration-300">
            <div className="text-5xl mb-4">🇮🇳</div>
            <h3 className="text-2xl font-bold text-white mb-3">India-First</h3>
            <p className="text-white text-opacity-80">
              Built for Indian privacy needs. Perfect for joint families.
            </p>
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-20 bg-white bg-opacity-10 backdrop-blur-md rounded-3xl p-12 max-w-4xl mx-auto border border-white border-opacity-20">
          <h2 className="text-3xl font-bold text-white mb-6 text-center">
            How LuvHive Mystery Match Works
          </h2>
          <div className="space-y-4 text-white text-lg">
            <p className="flex items-start gap-3">
              <span className="text-yellow-300 text-2xl">🎲</span>
              <span><strong>Get Matched:</strong> Find someone new based on age and interests. Their profile is hidden!</span>
            </p>
            <p className="flex items-start gap-3">
              <span className="text-yellow-300 text-2xl">💬</span>
              <span><strong>Chat to Unlock:</strong> 30 msgs → Request Gender | 60 → Request Age | 120 → Request Photo | 250 → Full Profile</span>
            </p>
            <p className="flex items-start gap-3">
              <span className="text-yellow-300 text-2xl">⏰</span>
              <span><strong>48-Hour Window:</strong> Each match expires in 2 days. Make every chat count!</span>
            </p>
            <p className="flex items-start gap-3">
              <span className="text-yellow-300 text-2xl">✨</span>
              <span><strong>Premium Option:</strong> Choose gender (👧 Find Girls or 👦 Find Boys), unlimited matches, instant reveals. Try 1 week for just ₹199!</span>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-16 text-center text-white text-opacity-80">
          <p>Safe • Anonymous • Privacy-Conscious • Made for India 🇮🇳</p>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;