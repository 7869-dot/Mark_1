import React from 'react';
import LiquidEther from './LiquidEther';
import { Atom, SquareActivity } from 'lucide-react';
import './App.css';

function App() {
  return (
    <div className="app-wrapper">
      <div className="background-layer" />
      
      <div className="liquid-ether">
        <LiquidEther
          colors={['#5227FF', '#FF9FFC', '#B19EEF']}
          mouseForce={20}
          cursorSize={100}
          isViscous
          viscous={30}
          iterationsViscous={32}
          iterationsPoisson={32}
          resolution={0.5}
          isBounce={false}
          dt={0.025}
          autoDemo
          autoSpeed={2.5}
          autoIntensity={5.0}
          takeoverDuration={0.25}
          autoResumeDelay={3000}
          autoRampDuration={0.6}
        />
      </div>

      <div className="ui-layer">
        <nav className="navbar">
          <div className="brand">
            <Atom className="brand-icon" size={22} />
            <span>React Bits</span>
          </div>
          <div className="nav-links">
            <a href="#home">Home</a>
            <a href="#docs">Docs</a>
          </div>
        </nav>

        <main className="hero">
          <button className="badge-btn">
            <SquareActivity size={14} strokeWidth={2} className="badge-icon" />
            New Background
          </button>
          
          <h1 className="main-title">
            The web, made fluid at<br />
            your fingertips.
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
