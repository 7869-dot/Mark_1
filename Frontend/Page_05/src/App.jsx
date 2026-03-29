import React, { useState, useRef, useEffect } from 'react';
import Orb from './Orb';
import { Plus, ChevronDown, AudioLines, Send } from 'lucide-react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isAgentThinking, setIsAgentThinking] = useState(false);
  const [aiThought, setAiThought] = useState(null); // 'thinking', 'response text', or null
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of chat history (user messages only)
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim() || isAgentThinking) return;

    // Add User Message
    const userMessage = { id: Date.now(), text: inputText, sender: 'user' };
    setMessages((prev) => [...prev, userMessage]);
    setInputText('');

    // Clear previous thought and trigger AI Thinking State
    setAiThought('thinking');
    setIsAgentThinking(true);

    // Simulate Network/Processing Delay
    setTimeout(() => {
      setIsAgentThinking(false);
      setAiThought("I'm thinking about that...");
    }, 5000);
  };

  return (
    <div className="app-container">
      <div className="orb-section">
        {aiThought && (
          <div className="thought-cloud-container">
            <div className="thought-cloud">
              {aiThought === 'thinking' ? (
                <div className="typing-indicator dark-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              ) : (
                <p className="thought-text">{aiThought}</p>
              )}
              <div className="thought-dot-1"></div>
              <div className="thought-dot-2"></div>
            </div>
          </div>
        )}
        <div className="orb-wrapper">
          <Orb
            hoverIntensity={2}
            rotateOnHover={true}
            hue={0}
            forceHoverState={isAgentThinking}
            backgroundColor="#000000"
          />
        </div>
      </div>

      <div className="chat-section">
        <div className="chat-history">
          {messages.length === 0 && (
            <div className="empty-state">
              <p>How can I help you today?</p>
            </div>
          )}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className="message-wrapper message-user"
            >
              <div className="message-bubble">{msg.text}</div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <form className="chat-form" onSubmit={handleSubmit}>
            <button
              type="button"
              className="icon-btn"
              aria-label="Add attachment"
            >
              <Plus size={20} />
            </button>
            <input
              type="text"
              className="chat-input"
              placeholder="Reply..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isAgentThinking}
            />
            <div className="input-actions">
              <div className="model-selector">
                <span className="model-text">Sonnet 4.6 Extended</span>
                <ChevronDown size={14} className="chevron" />
              </div>
              <button
                type={inputText.length > 0 ? "submit" : "button"}
                className={`icon-btn ${inputText.length > 0 ? 'active' : ''}`}
                disabled={isAgentThinking}
              >
                {inputText.length > 0 ? <Send size={20} /> : <AudioLines size={20} />}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
