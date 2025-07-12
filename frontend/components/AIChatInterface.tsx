// components/AIChatInterface.tsx
"use client";

import { useState, useEffect } from "react";

// Define a type for messages
interface Message {
  text: string;
  sender: "user" | "ai";
  timestamp: string;
}

export default function AIChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [conversationId] = useState<string>(Date.now().toString());
  const [isTyping, setIsTyping] = useState(false);

  const clearChat = () => {
    setMessages([]);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const newMessage: Message = {
      text: input,
      sender: "user",
      timestamp: new Date().toISOString(),
    };

    setMessages([...messages, newMessage]);
    setIsTyping(true);

    try {
      const response = await fetch("/api/ai-query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: input,
          conversation_id: conversationId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setIsTyping(false);
        setMessages((prev) => [
          ...prev,
          {
            text: data.response,
            sender: "ai",
            timestamp: new Date().toISOString(),
          },
        ]);
      } else {
        const errorData = await response.json();
        setIsTyping(false);
        setMessages((prev) => [
          ...prev,
          {
            text: `Error: ${errorData.detail || "Failed to get AI response"}`,
            sender: "ai",
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    } catch (error) {
      console.error("Network error:", error);
      setIsTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          text: "Network error. Please check if the backend server is running.",
          sender: "ai",
          timestamp: new Date().toISOString(),
        },
      ]);
    }

    setInput("");
  };

  // Typing indicator component
  const TypingIndicator = () => (
    <div className="message-ai">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 text-2xl">
          🤖
        </div>
        <div className="flex-1">
          <div className="text-sm opacity-70 mb-1">
            AI Assistant
          </div>
          <div className="flex items-center gap-2">
            <span className="text-gray-400">AI is thinking</span>
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-[#ff1801] rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-[#ff1801] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-[#ff1801] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8 text-gradient">
          AI F1 Assistant
        </h1>
        
        <div className="card mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${isTyping ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`}></div>
              <span className="text-lg font-medium">
                {isTyping ? 'AI is responding...' : 'Conversation Active'}
              </span>
            </div>
            <button
              onClick={clearChat}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors text-sm"
              disabled={isTyping}
            >
              Clear Chat
            </button>
          </div>
          <div className="mt-3 text-sm text-gray-400">
            I'll remember our conversation context throughout our chat
          </div>
        </div>

        <div className="card p-6 h-[500px] overflow-y-auto mb-6 bg-gradient-to-b from-[#1e1e1e] to-[#2a2a2a]">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="text-6xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold mb-2 text-gray-300">
                Welcome to the AI F1 Assistant
              </h3>
              <p className="text-gray-400 max-w-md">
                Ask me anything about F1 regulations, rules, or technical specifications. 
                I'll remember our conversation context and can answer follow-up questions.
              </p>
              <div className="mt-6 text-sm text-gray-500">
                🔄 Conversation mode: I'll remember our chat context
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`${
                    message.sender === "user" ? "message-user" : "message-ai"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 text-2xl">
                      {message.sender === "user" ? "👤" : "🤖"}
                    </div>
                    <div className="flex-1">
                      <div className="text-sm opacity-70 mb-1">
                        {message.sender === "user" ? "You" : "AI Assistant"}
                      </div>
                      <div className="whitespace-pre-wrap">{message.text}</div>
                    </div>
                  </div>
                </div>
              ))}
              {isTyping && <TypingIndicator />}
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="card p-4">
          <div className="flex gap-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="form-input flex-1 text-lg"
              placeholder="Ask about F1 regulations, rules, or technical specifications..."
              disabled={isTyping}
            />
            <button 
              type="submit" 
              className="racing-button px-8 py-3 text-lg"
              disabled={!input.trim() || isTyping}
            >
              {isTyping ? 'Sending...' : 'Send 🚀'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
