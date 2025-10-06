import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-pink-100">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center animate-fadeIn">
          <h1 className="text-6xl md:text-7xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-600 via-rose-500 to-pink-600 mb-6">
            Welcome to LuvHive
          </h1>
          <p className="text-xl md:text-2xl text-gray-700 mb-4 max-w-3xl mx-auto">
            Your Anonymous Dating & Social World
          </p>
          <p className="text-lg text-gray-600 mb-12 max-w-2xl mx-auto">
            Connect, share stories, and chat anonymously with people around the world. 
            Join LuvHive - where connections are real and identities are yours to reveal.
          </p>
          
          <div className="flex gap-4 justify-center flex-wrap">
            <Link to="/register">
              <Button 
                data-testid="get-started-btn"
                className="bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white px-8 py-6 text-lg rounded-full btn-hover"
              >
                Enter LuvHive
              </Button>
            </Link>
            <Link to="/login">
              <Button 
                data-testid="login-btn"
                variant="outline" 
                className="border-2 border-pink-500 text-pink-600 hover:bg-pink-50 px-8 py-6 text-lg rounded-full btn-hover"
              >
                Sign In
              </Button>
            </Link>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-24 grid md:grid-cols-3 gap-8 animate-slideIn">
          <div className="glass-effect rounded-3xl p-8 text-center hover:shadow-xl transition-all duration-300">
            <div className="text-5xl mb-4">📸</div>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">Share Stories</h3>
            <p className="text-gray-600">
              Share your moments with 24-hour stories, just like your favorite social apps
            </p>
          </div>

          <div className="glass-effect rounded-3xl p-8 text-center hover:shadow-xl transition-all duration-300">
            <div className="text-5xl mb-4">💬</div>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">Anonymous Chat</h3>
            <p className="text-gray-600">
              Connect and chat anonymously. Upgrade to premium for unlimited conversations
            </p>
          </div>

          <div className="glass-effect rounded-3xl p-8 text-center hover:shadow-xl transition-all duration-300">
            <div className="text-5xl mb-4">🎭</div>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">Dating & Social</h3>
            <p className="text-gray-600">
              Discover new connections in a safe, anonymous environment
            </p>
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-20 glass-effect rounded-3xl p-12 max-w-4xl mx-auto animate-scaleIn">
          <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
            Why LuvHive?
          </h2>
          <div className="space-y-4 text-gray-700 text-lg">
            <p className="flex items-start gap-3">
              <span className="text-pink-500 text-2xl">✓</span>
              <span><strong>Anonymous & Safe:</strong> Your privacy is our priority. Share as much or as little as you want.</span>
            </p>
            <p className="flex items-start gap-3">
              <span className="text-pink-500 text-2xl">✓</span>
              <span><strong>Telegram Integrated:</strong> Seamlessly connected with our Telegram bot for premium features.</span>
            </p>
            <p className="flex items-start gap-3">
              <span className="text-pink-500 text-2xl">✓</span>
              <span><strong>Real Connections:</strong> Meet genuine people looking for friendship, dating, or just a chat.</span>
            </p>
            <p className="flex items-start gap-3">
              <span className="text-pink-500 text-2xl">✓</span>
              <span><strong>Premium Benefits:</strong> Unlock unlimited chat and exclusive features with premium membership.</span>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-16 text-center text-gray-600">
          <p>Connected with Telegram Bot • Safe • Anonymous • Fun</p>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;