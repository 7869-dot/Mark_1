import React from 'react';
import LiquidEther from './LiquidEther';
import CardSwap, { Card } from './CardSwap';
import GooeyNav from './GooeyNav';
import Shuffle from './Shuffle';
import SpotlightCard from './SpotlightCard';
import Footer from './Footer';
import ScrollReveal from './ScrollReveal';
import { SquareActivity, SlidersHorizontal, Circle, Code, ChevronDown, Sparkles, Activity, Shield, Zap, Target } from 'lucide-react';
import './App.css';

function App() {
  const navItems = [
    { label: "Research", href: "#research" },
    { label: "Economic Futures", href: "#economic-futures" },
    { label: <span style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>Commitments <ChevronDown size={14} /></span>, href: "#commitments" },
    { label: <span style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>Learn <ChevronDown size={14} /></span>, href: "#learn" },
    { label: "News", href: "#news" },
  ];

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
            <span>SHADOW</span>
          </div>
          <div className="nav-links" style={{ gap: 0, marginTop: '2px' }}>
            <GooeyNav
              items={navItems}
              initialActiveIndex={0}
            />
          </div>
          <div className="nav-actions">
            <button className="btn-try">
              Try Shadow
              <div className="btn-try-divider" />
              <ChevronDown size={16} />
            </button>
          </div>
        </nav>

        <main className="hero">
          <div className="main-title-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0', marginBottom: '3rem' }}>
            <h1 className="main-title" style={{ marginBottom: 0 }}>
              <Shuffle
                text="Shadow"
                shuffleDirection="right"
                duration={0.35}
                animationMode="evenodd"
                shuffleTimes={1}
                ease="power3.out"
                stagger={0.03}
                threshold={0.1}
                triggerOnce={true}
                triggerOnHover={true}
                respectReducedMotion={true}
                loop={false}
                loopDelay={0}
              />
            </h1>
            <p className="tagline">The self you buried is the one we built</p>
          </div>

          <div className="hero-actions">
            <button className="btn-primary">Get Started</button>
            <button className="btn-secondary">Learn More</button>
          </div>
        </main>

        <section className="section-scrolltext">
          <ScrollReveal
            baseOpacity={0.1}
            enableBlur={true}
            baseRotation={0}
            blurStrength={4}
          >
            We're building a second consciousness that lives inside a screen and is made entirely out of you. It is a living psychological portrait of you — assembled silently over time — that has developed its own voice ---&gt; That is your Inner voice. It knows you the way only you know you. It doesn't say "you're doing great." It says the thing underneath that — the thing you actually needed to hear that nobody in your life has the precision to say.
          </ScrollReveal>
        </section>

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

        <section className="section-spotlight">
          <div className="spotlight-row-top">
            <SpotlightCard className="custom-spotlight-card" spotlightColor="rgba(255, 255, 255, 0.15)">
              <Sparkles size={32} color="#ffffff" style={{ marginBottom: '1.5rem', opacity: 0.9 }} />
              <h3 className="spotlight-title">Boost Your Experience</h3>
              <p className="spotlight-text">Get exclusive benefits, features & 24/7 support as a permanent club member.</p>
            </SpotlightCard>
            <SpotlightCard className="custom-spotlight-card" spotlightColor="rgba(255, 255, 255, 0.15)">
              <Activity size={32} color="#ffffff" style={{ marginBottom: '1.5rem', opacity: 0.9 }} />
              <h3 className="spotlight-title">Actionable Analytics</h3>
              <p className="spotlight-text">Gain deep insights into your growth with real-time actionable data graphs.</p>
            </SpotlightCard>
            <SpotlightCard className="custom-spotlight-card" spotlightColor="rgba(255, 255, 255, 0.15)">
              <Shield size={32} color="#ffffff" style={{ marginBottom: '1.5rem', opacity: 0.9 }} />
              <h3 className="spotlight-title">Ironclad Platform</h3>
              <p className="spotlight-text">Your privacy protected through cutting-edge, bank-grade encryption layers.</p>
            </SpotlightCard>
          </div>
          <div className="spotlight-row-bottom">
            <SpotlightCard className="custom-spotlight-card" spotlightColor="rgba(255, 255, 255, 0.15)">
              <Zap size={32} color="#ffffff" style={{ marginBottom: '1.5rem', opacity: 0.9 }} />
              <h3 className="spotlight-title">Lighting Precision</h3>
              <p className="spotlight-text">Our optimized global edge network delivers sub-millisecond deployment.</p>
            </SpotlightCard>
            <SpotlightCard className="custom-spotlight-card" spotlightColor="rgba(255, 255, 255, 0.15)">
              <Target size={32} color="#ffffff" style={{ marginBottom: '1.5rem', opacity: 0.9 }} />
              <h3 className="spotlight-title">Absolute Control</h3>
              <p className="spotlight-text">Target everything flawlessly using an expansive suite of intelligent filters.</p>
            </SpotlightCard>
          </div>
        </section>

        <Footer />
      </div>
    </div>
  );
}

export default App;
