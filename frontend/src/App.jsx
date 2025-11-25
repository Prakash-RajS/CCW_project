import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Testing from "./pages/Testing";
import SignUp from "./pages/Authontication/SignUp";


export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Testing />} />
        <Route path="/signup" element={<SignUp />} />  {/* Fixed: lowercase */}
        <Route path="*" element={<div>404 Not Found</div>} />
      </Routes>
    </Router>
  );
}