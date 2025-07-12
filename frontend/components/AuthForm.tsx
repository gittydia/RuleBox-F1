"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function AuthForm({ type = "login" }) {
  const router = useRouter();

  const [formData, setFormData] = useState({
    username: "",
    password: "",
    email: "",
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const endpoint = type === "login" ? "http://localhost:8000/auth/login" : "http://localhost:8000/auth/register";

    try {
      console.log("Making request to:", endpoint);
      console.log("Form data:", formData);
      
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      console.log("Response status:", response.status);
      console.log("Response ok:", response.ok);
      console.log("Response headers:", Object.fromEntries(response.headers.entries()));

      if (response.ok) {
        const data = await response.json();
        console.log("Success response:", data);
        
        if (type === "login") {
          localStorage.setItem("token", data.token);
          router.push("/");
        } else {
          // Registration successful
          alert("Registration successful! You can now sign in.");
          router.push("/auth/login");
        }
      } else {
        // Try to get error response
        const contentType = response.headers.get("content-type");
        console.log("Error response content type:", contentType);
        
        if (contentType && contentType.includes("application/json")) {
          try {
            const errorData = await response.json();
            console.error("Authentication failed:", errorData);
            
            // Handle empty or malformed error responses
            let errorMessage = "Authentication failed";
            if (errorData && typeof errorData === 'object') {
              if (errorData.detail) {
                errorMessage = errorData.detail;
              } else if (errorData.message) {
                errorMessage = errorData.message;
              } else if (errorData.error) {
                errorMessage = errorData.error;
              } else if (Object.keys(errorData).length === 0) {
                // Empty object - provide status-based message
                errorMessage = response.status === 401 
                  ? "Invalid credentials. Please check your username and password."
                  : response.status === 400 
                  ? "Invalid request. Please check your input."
                  : `Authentication failed (${response.status})`;
              }
            }
            
            alert(errorMessage);
          } catch (jsonError) {
            console.error("Failed to parse JSON error response:", jsonError);
            alert("Authentication failed. Server returned invalid response.");
          }
        } else {
          const errorText = await response.text();
          console.error("Authentication failed with non-JSON response:", errorText);
          alert(`Authentication failed. Server error: ${response.status}`);
        }
      }
    } catch (error) {
      console.error("Network error:", error);
      alert("Network error. Please check if the backend server is running.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full">
        <div className="card">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gradient mb-2">
              RuleBox F1
            </h1>
            <h2 className="text-2xl font-semibold text-white">
              {type === "login" ? "Welcome Back" : "Create Account"}
            </h2>
            <p className="text-gray-400 mt-2">
              {type === "login" 
                ? "Sign in to access F1 regulations" 
                : "Join the F1 regulation community"
              }
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Username
              </label>
              <input
                type="text"
                placeholder="Enter your username"
                value={formData.username}
                onChange={(e) =>
                  setFormData({ ...formData, username: e.target.value })
                }
                className="form-input"
                required
              />
            </div>

            {type === "register" && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  className="form-input"
                  required
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                type="password"
                placeholder="Enter your password"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                className="form-input"
                required
              />
            </div>

            <button type="submit" className="racing-button w-full text-lg py-3">
              {type === "login" ? "Sign In" : "Create Account"}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-400">
              {type === "login" ? "Don't have an account?" : "Already have an account?"}
            </p>
            <Link 
              href={type === "login" ? "/auth/register" : "/auth/login"} 
              className="text-[#ff1801] hover:text-[#cc1401] font-medium transition-colors"
            >
              {type === "login" ? "Create one here" : "Sign in instead"}
            </Link>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-10 left-10 w-20 h-20 border-2 border-[#ff1801] rounded-full opacity-20 animate-pulse"></div>
        <div className="absolute bottom-10 right-10 w-16 h-16 border-2 border-[#ff1801] rounded-full opacity-20 animate-pulse delay-300"></div>
      </div>
    </div>
  );
}
