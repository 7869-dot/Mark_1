import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to the bottom of the chat history
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    // Add user message to chat immediately
    const userMessage = { id: Date.now(), text: inputText, sender: 'user' };
    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Send user message to the FastAPI backend
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: userMessage.text,
          user_id: 'default_user'
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();

      // Support both "response" (from generic spec) and "reply" (from backend main.py schema)
      const botText = data.response || data.reply || "No response received.";

      const botMessage = { id: Date.now() + 1, text: botText, sender: 'bot' };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error fetching bot response:', error);
      // Fallback message connecting to root if /api/chat isn't the correct route 
      // but testing the standard local spec connection anyway
      const errorMessage = { id: Date.now() + 1, text: "Error: Could not connect to backend.", sender: 'bot' };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="chat-container">
        <header className="chat-header">
          <h1>AI Chatbot</h1>
        </header>

        <div className="chat-history">
          {messages.length === 0 && (
            <div className="empty-state">
              <p>Say hello to start the conversation!</p>
            </div>
          )}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`message-wrapper ${msg.sender === 'user' ? 'message-user' : 'message-bot'}`}
            >
              <div className="message-bubble">{msg.text}</div>
            </div>
          ))}
          {/* Loading Indicator */}
          {isLoading && (
            <div className="message-wrapper message-bot">
              <div className="message-bubble">
                <div className="typing-indicator dark-dots">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <form className="chat-form" onSubmit={handleSubmit}>
            <input
              type="text"
              className="chat-input"
              placeholder="Type your message..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isLoading}
            />
            <button
              type="submit"
              className="send-button"
              disabled={isLoading || !inputText.trim()}
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
