import React from 'react';
import './Hero.css';

const Hero = () => {
  return (
    <section id="home" className="hero-section">
      <div className="hero-background">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
      </div>
      <div className="hero-content animate-fade-in">
        <div className="badge">Trusted by 10k+ Families</div>
        <h1 className="hero-title">
          Protect Your Future with <br/>
          <span className="text-gradient">Complete Certainty</span>
        </h1>
        <p className="hero-subtitle">
          Experience personalized insurance solutions designed to protect everything you love with absolute peace of mind.
        </p>
        <div className="hero-cta">
          <button className="btn btn-primary btn-lg">Explore Plans</button>
          <button className="btn btn-outline btn-lg">Watch Video</button>
        </div>
      </div>
    </section>
  );
};

export default Hero;
