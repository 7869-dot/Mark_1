import React from 'react';
import './LoginUI.css';

export default function LoginUI() {
  return (
    <div className="login-container">
      <div className="login-header">
        <div className="logo-area">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="brand-logo">
            <path d="M12 2L12 22M2 12H22M4.93 4.93L19.07 19.07M4.93 19.07L19.07 4.93" stroke="#e6dbd1" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <span className="brand-text">Claude</span>
        </div>
        
        <h1 className="main-headline">Think fast,<br />build faster</h1>
        <p className="sub-headline">Brainstorm in Claude, build in Cowork</p>
      </div>

      <div className="login-card">
        <button className="btn-provider btn-google">
          <svg className="google-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.1c-.22-.66-.35-1.36-.35-2.1s.13-1.44.35-2.1V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l3.66-2.84z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/>
          </svg>
          <span className="btn-text">Continue with Google</span>
        </button>

        <div className="divider">
          <span>OR</span>
        </div>

        <div className="form-group">
          <input type="email" placeholder="Enter your email" className="input-field" />
        </div>

        <button className="btn-primary">
          Continue with email
        </button>
      </div>

      <div className="footer-actions">
        <button className="btn-download">
          <svg className="download-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
            <line x1="8" y1="21" x2="16" y2="21"></line>
            <line x1="12" y1="17" x2="12" y2="21"></line>
          </svg>
          Download desktop app
        </button>
      </div>
    </div>
  );
}
