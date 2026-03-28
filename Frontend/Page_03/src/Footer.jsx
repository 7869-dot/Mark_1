import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="site-footer">
      <div className="footer-container">
        
        {/* Column 1: Brand & Social */}
        <div className="footer-col brand-col">
          <div className="brand-logo">SHADOW</div>
          <div className="copyright">© 2026 SHADOW PBC</div>
          <div className="social-links">
            <a href="#">
              <svg fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
            </a>
            <a href="#">
              <svg fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.5h1.833L7.084 4.126H5.117z"/></svg>
            </a>
            <a href="#">
              <svg fill="currentColor" viewBox="0 0 24 24"><path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/></svg>
            </a>
          </div>
        </div>

        {/* Links Grid */}
        <div className="footer-links-grid">
          {/* Column 2: Products */}
          <div className="footer-col">
            <h3>Products</h3>
            <a href="#">Shadow Core</a>
            <a href="#">Shadow AI</a>
            <a href="#">Shadow Enterprise</a>
            <a href="#">Console login</a>
          </div>

          {/* Column 3: Solutions */}
          <div className="footer-col">
            <h3>Solutions</h3>
            <a href="#">AI Agents</a>
            <a href="#">Code Security</a>
            <a href="#">Code Modernization</a>
            <a href="#">Customer Support</a>
            <a href="#">Financial Services</a>
          </div>

          {/* Column 4: Resources */}
          <div className="footer-col">
            <h3>Resources</h3>
            <a href="#">Blog & News</a>
            <a href="#">Partner Network</a>
            <a href="#">Community</a>
            <a href="#">Engineering Docs</a>
            <a href="#">Events</a>
          </div>

          {/* Column 5: Support & Legal */}
          <div className="footer-col">
            <h3>Company</h3>
            <a href="#">About Us</a>
            <a href="#">Support Center</a>
            <a href="#">System Status</a>
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
          </div>
        </div>

      </div>
    </footer>
  );
};

export default Footer;
