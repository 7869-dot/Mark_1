import React from 'react';
import Orb from './Orb';

function App() {
  return (
    <div className="app-container">
      {/* Background Orb */}
      <div className="orb-background">
        <Orb
          hoverIntensity={2}
          rotateOnHover={true}
          hue={0}
          forceHoverState={false}
          backgroundColor="#050505"
        />
      </div>

      {/* Foreground Content */}
      <div className="content-overlay">
        {/* Navigation Bar */}
        <nav className="navbar">
          <div className="nav-logo">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="3" stroke="white" strokeWidth="1.5"/>
              <ellipse cx="12" cy="12" rx="10" ry="3.5" stroke="white" strokeWidth="1.5" transform="rotate(30 12 12)"/>
              <ellipse cx="12" cy="12" rx="10" ry="3.5" stroke="white" strokeWidth="1.5" transform="rotate(-30 12 12)"/>
              <ellipse cx="12" cy="12" rx="10" ry="3.5" stroke="white" strokeWidth="1.5" transform="rotate(90 12 12)"/>
            </svg>
            <span>React Bits</span>
          </div>
          <div className="nav-links">
            <a href="#">Home</a>
            <a href="#">Docs</a>
          </div>
        </nav>

        {/* Hero Section */}
        <main className="hero">
          <button className="badge-button">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
            New Background
          </button>
          
          <h1 className="hero-title">
            This orb is hiding<br/>something, try hovering!
          </h1>
          
          <div className="hero-actions">
            <button className="btn-primary">Get Started</button>
            <button className="btn-secondary">Learn More</button>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
