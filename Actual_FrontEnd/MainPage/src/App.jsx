import { useState, useRef } from 'react';
import './App.css';

function App() {
  const [activeItem, setActiveItem] = useState('New chat');
  const textAreaRef = useRef(null);

  const handleInput = (e) => {
    e.target.style.height = 'auto';
    e.target.style.height = `${e.target.scrollHeight}px`;
  };

  const menuItems = [
    { id: 'New chat', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg> },
    { id: 'Search', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg> },
    { id: 'Chats', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg> }
  ];

  const recentItems = [
    "History01",
    "History02",
    "History03",
    "History04",
    "History05",
    "History06",
    "History07",
    "History08",
    "History09",
    "History10"
  ];

  const chips = [
    { label: 'Code', icon: <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg> },
    { label: 'Learn', icon: <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 10v6M2 10l10-5 10 5-10 5z"></path><path d="M6 12v5c3 3 9 3 12 0v-5"></path></svg> },
    { label: 'Create', icon: <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg> },
    { label: 'Write', icon: <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg> },
    { label: 'Life stuff', icon: <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg> },
  ];

  return (
    <div id="app-container">
      {/* Section 1: Left Panel */}
      <aside id="sidebar">
        <div className="sidebar-top">
          <div className="logo" style={{ marginBottom: '24px', paddingLeft: '4px' }}>
            <h2>Axotol</h2>
          </div>
          
          <nav className="main-nav">
            {menuItems.map(item => (
              <a 
                href="#" 
                key={item.id}
                className={`nav-item ${activeItem === item.id ? 'active' : ''}`}
                onClick={(e) => { e.preventDefault(); setActiveItem(item.id); }}
              >
                {item.icon}
                {item.id}
              </a>
            ))}
          </nav>

          <div className="divider"></div>

          <div className="recents-section">
            <h3 className="section-title">Recents</h3>
            <div className="recent-list">
              {recentItems.map((item, idx) => (
                <a 
                  href="#" 
                  key={idx}
                  className={`recent-item ${activeItem === `recent-${idx}` ? 'active' : ''}`}
                  onClick={(e) => { e.preventDefault(); setActiveItem(`recent-${idx}`); }}
                >
                  {item}
                </a>
              ))}
            </div>
          </div>
        </div>

        <div className="sidebar-bottom">
          <div className="user-profile">
            <div className="user-avatar">P</div>
            <div className="user-info">
              <div className="user-name">Pr1smVoid6</div>
              <div className="user-plan">Free plan</div>
            </div>
            <button className="icon-button profile-options" aria-label="Profile options">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="1"></circle><circle cx="12" cy="5" r="1"></circle><circle cx="12" cy="19" r="1"></circle></svg>
            </button>
          </div>
        </div>
      </aside>

      {/* Sections 2, 3, 4: Splitting the main area */}
      <div id="main-wrapper">
        <div className="middle-panel">
          
          {/* SECTION 2: Top Middle Area */}
          <section className="section-2">
            <div className="bottom-bar">
              <div className="input-container-wrapper">
                <div className="quick-actions">
                  {chips.map((chip, idx) => (
                    <button key={idx} className="chip" onClick={(e) => e.preventDefault()}>
                      {chip.icon} {chip.label}
                    </button>
                  ))}
                </div>

                <div className="chat-input-box">
                  <textarea 
                    ref={textAreaRef}
                    placeholder="How can I help you today?" 
                    rows="1" 
                    onInput={handleInput}
                  ></textarea>
                  
                  <div className="input-controls">
                    <button className="icon-button attach-btn" aria-label="Attachment">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
                      </svg>
                    </button>
                    
                    <div className="right-controls">
                      <div className="model-selector">
                        <span>Sonnet 4.6</span> <span className="dim">Extended</span>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
                      </div>
                      <button className="send-btn" aria-label="Send">
                        <div className="bars">||||</div>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* SECTION 3: Bottom Middle Area */}
          <section className="section-3">
            {/* Blank for now */}
          </section>

        </div>

        {/* SECTION 4: Right Sidebar */}
        <aside className="section-4">
          <header className="main-header" style={{ position: 'absolute', top: 0, right: 0, width: '100%' }}>
            <div className="header-right">
              <button className="icon-button ghost-icon" aria-label="Ghost">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"></path></svg>
              </button>
            </div>
          </header>
        </aside>
      </div>
    </div>
  );
}

export default App;
