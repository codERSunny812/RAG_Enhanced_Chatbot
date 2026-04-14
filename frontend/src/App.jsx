import React from 'react';
import Navbar from './components/Navbar/Navbar';
import Hero from './components/Hero/Hero';
import Features from './components/Features/Features';
import Testimonials from './components/Testimonials/Testimonials';
import Chatbot from './components/Chatbot/Chatbot';

function App() {
  return (
    <div className="app-container">
      <Navbar />
      <main>
        <Hero />
        <Features />
        <Testimonials />
      </main>
      
      {/* Footer Section */}
      <footer style={{ background: 'var(--primary)', color: 'white', padding: '40px 20px', textAlign: 'center' }}>
        <p>© 2026 Stellar Insure Company - Protecting Your Future.</p>
      </footer>

      {/* Floating Chatbot Widget */}
      <Chatbot />
    </div>
  );
}

export default App;
