import React, { useState, useEffect } from 'react';
import { Shield } from 'lucide-react';
import './Navbar.css';

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`navbar ${scrolled ? 'glass' : ''}`}>
      <div className="nav-container">
        <a href="#" className="logo">
          <Shield className="logo-icon" size={32} />
          <span className="logo-text">Stellar Insure</span>
        </a>
        <div className="nav-links">
          <a href="#home">Home</a>
          <a href="#features">Services</a>
          <a href="#reviews">Reviews</a>
        </div>
        <div className="nav-actions">
          <a href="#quote" className="btn btn-primary">Get a Quote</a>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
