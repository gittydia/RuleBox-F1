import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0d0d0d] via-[#1a1a1a] to-[#0d0d0d]">
      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center min-h-[80vh] px-4 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-6xl md:text-8xl font-bold mb-6 text-gradient">
            RuleBox F1
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-4 max-w-2xl mx-auto">
            Your AI-powered Formula 1 regulation assistant
          </p>
          <p className="text-lg text-gray-400 mb-12 max-w-3xl mx-auto">
            Navigate the complex world of F1 regulations with intelligent search, AI-powered chat, and comprehensive rule analysis
          </p>

          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
            <Link href="/query" className="racing-button text-lg px-8 py-4">
              🔍 Search Rules
            </Link>
            <Link href="/ai-chat" className="racing-button text-lg px-8 py-4">
              🤖 AI Assistant
            </Link>
          </div>
        </div>

        {/* Animated Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          <div className="absolute top-40 right-20 w-1 h-1 bg-red-400 rounded-full animate-pulse delay-300"></div>
          <div className="absolute bottom-40 left-20 w-1 h-1 bg-red-600 rounded-full animate-pulse delay-700"></div>
          <div className="absolute bottom-20 right-10 w-2 h-2 bg-red-500 rounded-full animate-pulse delay-500"></div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-16 text-gradient">
            Powerful Features
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="card glass-effect text-center">
              <div className="text-5xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold mb-4 text-[#ff1801]">Smart Search</h3>
              <p className="text-gray-300">
                Advanced search through F1 regulations with intelligent filtering and categorization
              </p>
              <Link href="/query" className="inline-block mt-4 text-[#ff1801] hover:underline">
                Try Search →
              </Link>
            </div>

            <div className="card glass-effect text-center">
              <div className="text-5xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold mb-4 text-[#ff1801]">AI Assistant</h3>
              <p className="text-gray-300">
                Chat with our AI to get explanations, interpretations, and answers about F1 rules
              </p>
              <Link href="/ai-chat" className="inline-block mt-4 text-[#ff1801] hover:underline">
                Start Chat →
              </Link>
            </div>

            <div className="card glass-effect text-center">
              <div className="text-5xl mb-4">📖</div>
              <h3 className="text-xl font-semibold mb-4 text-[#ff1801]">Comprehensive Database</h3>
              <p className="text-gray-300">
                Access to sporting, technical, financial, and operational regulations all in one place
              </p>
              <Link href="/auth/login" className="inline-block mt-4 text-[#ff1801] hover:underline">
                Get Started →
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-[#ff1801]/10 to-transparent">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-12 text-gradient">
            Why Choose RuleBox F1?
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="card">
              <div className="text-3xl font-bold text-[#ff1801] mb-2">100+</div>
              <p className="text-gray-300">Regulation Categories</p>
            </div>
            <div className="card">
              <div className="text-3xl font-bold text-[#ff1801] mb-2">24/7</div>
              <p className="text-gray-300">AI Assistant Available</p>
            </div>
            <div className="card">
              <div className="text-3xl font-bold text-[#ff1801] mb-2">Instant</div>
              <p className="text-gray-300">Search Results</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
