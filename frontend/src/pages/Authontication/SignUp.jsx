import React from "react";
import { Link } from "react-router-dom";

const SignUp = () => {
  return (
    <section
      className="relative w-full min-h-screen flex justify-center items-center bg-black text-white overflow-hidden"
    
    >
      {/* Dark Overlay for better text readability */}
      <div className="absolute inset-0 bg-black opacity-70"></div>

      {/* Optional: A subtle gradient overlay for extra depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900 via-black to-black opacity-60"></div>

      {/* Content */}
      <div className="relative z-10 bg-white text-black p-10 md:p-12 rounded-2xl shadow-2xl max-w-md w-full mx-4">
        <h1 className="text-4xl font-extrabold mb-2 text-center bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          Create Account
        </h1>
        <p className="text-center text-blue-600 mb-8">Join us today!</p>

        {/* Your form will go here later */}
        <div className="space-y-6">
          <input
            type="text"
            placeholder="Full Name"
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-600"
          />
          <input
            type="email"
            placeholder="Email"
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-600"
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-600"
          />
          <button className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-4 rounded-lg hover:opacity-90 transition">
            Sign Up
          </button>
        </div>

        <p className="text-center mt-6 text-gray-600">
          Already have an account?{" "}
          <Link to="/" className="text-purple-600 font-semibold hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </section>
  );
};

export default SignUp;