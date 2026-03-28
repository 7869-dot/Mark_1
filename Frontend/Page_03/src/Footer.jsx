import React from 'react';
import { Linkedin, Twitter, Youtube } from 'lucide-react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="site-footer">
      <div className="footer-container">
        <div className="footer-top">
          <div className="footer-brand">
            <span className="brand-logo">SHADOW</span>
          </div>
          <div className="footer-links-grid">
            <div className="footer-column">
              <h4>Products</h4>
              <ul>
                <li><a href="#">Shadow Core</a></li>
                <li><a href="#">Shadow Code</a></li>
                <li><a href="#">Shadow Enterprise</a></li>
                <li><a href="#">Shadow Cowork</a></li>
                <li><a href="#">Shadow for Chrome</a></li>
                <li><a href="#">Shadow for Excel</a></li>
                <li><a href="#">Shadow for Slack</a></li>
              </ul>
            </div>
            <div className="footer-column">
              <h4>Solutions</h4>
              <ul>
                <li><a href="#">AI agents</a></li>
                <li><a href="#">Shadow Code Security</a></li>
                <li><a href="#">Code modernization</a></li>
                <li><a href="#">Coding</a></li>
                <li><a href="#">Customer support</a></li>
                <li><a href="#">Education</a></li>
                <li><a href="#">Financial services</a></li>
                <li><a href="#">Government</a></li>
                <li><a href="#">Healthcare</a></li>
              </ul>
            </div>
            <div className="footer-column">
              <h4>Resources</h4>
              <ul>
                <li><a href="#">Blog</a></li>
                <li><a href="#">Shadow partner network</a></li>
                <li><a href="#">Community</a></li>
                <li><a href="#">Connectors</a></li>
                <li><a href="#">Courses</a></li>
                <li><a href="#">Customer stories</a></li>
                <li><a href="#">Engineering</a></li>
                <li><a href="#">Events</a></li>
              </ul>
            </div>
            <div className="footer-column">
              <h4>Help and security</h4>
              <ul>
                <li><a href="#">Availability</a></li>
                <li><a href="#">Status</a></li>
                <li><a href="#">Support center</a></li>
              </ul>
              <h4 style={{ marginTop: '2.5rem' }}>Terms and policies</h4>
              <ul>
                <li><a href="#">Privacy choices</a></li>
                <li><a href="#">Privacy policy</a></li>
                <li><a href="#">Consumer health data privacy policy</a></li>
              </ul>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="footer-bottom-left">
            <p>© 2026 Shadow Corp</p>
            <div className="social-links">
              <a href="#"><Linkedin size={18} /></a>
              <a href="#"><Twitter size={18} /></a>
              <a href="#"><Youtube size={18} /></a>
            </div>
          </div>
          <div className="footer-bottom-right">
            <div className="bottom-links-column">
              <ul>
                <li><a href="#">Haiku</a></li>
              </ul>
            </div>
            <div className="bottom-links-column">
              <ul>
                <li><a href="#">Google Cloud's Vertex AI</a></li>
                <li><a href="#">Microsoft Foundry</a></li>
                <li><a href="#">Console login</a></li>
              </ul>
            </div>
            <div className="bottom-links-column">
              <ul>
                <li><a href="#">Economic Futures</a></li>
                <li><a href="#">Research</a></li>
                <li><a href="#">News</a></li>
                <li><a href="#">Constitution</a></li>
                <li><a href="#">Responsible Scaling Policy</a></li>
                <li><a href="#">Security and compliance</a></li>
                <li><a href="#">Transparency</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
