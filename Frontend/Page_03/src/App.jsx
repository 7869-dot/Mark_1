import React from 'react';
import LiquidEther from './LiquidEther';
import CardSwap, { Card } from './CardSwap';
import { Atom, SquareActivity, SlidersHorizontal, Circle, Code } from 'lucide-react';
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

        <section className="section-cards">
          <div className="cards-content">
            <div className="cards-text">
              <h2 className="cards-title">
                Card stacks <span className="highlight">have never</span> <span className="highlight">looked so good</span>
              </h2>
              <p className="cards-subtitle">Just look at it go!</p>
            </div>
            
            <div className="cards-wrapper">
              <CardSwap cardDistance={30} verticalDistance={40} delay={4000} pauseOnHover={false}>
                <Card>
                  <div className="card-header">
                    <SlidersHorizontal size={14} /> Customizable
                  </div>
                  <div className="card-content">
                    <span className="card-number">1</span>
                  </div>
                </Card>
                <Card>
                  <div className="card-header">
                    <Circle size={14} fill="currentColor" /> Smooth
                  </div>
                  <div className="card-content">
                    <span className="card-number">2</span>
                  </div>
                </Card>
                <Card>
                  <div className="card-header">
                    <Code size={14} /> Reliable
                  </div>
                  <div className="card-content">
                    <span className="card-number">3</span>
                  </div>
                </Card>
              </CardSwap>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;
