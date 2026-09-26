import React from 'react';
import { Link } from 'react-router-dom';
import { companyInfo } from '../data';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-gray-300 py-12 relative overflow-hidden">
      {/* Background image for footer */}
      <div className="absolute inset-0 z-0 opacity-10">
        <img src="/assets/footer-image.jpg" alt="Footer Background" className="w-full h-full object-cover" />
      </div>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-white text-xl font-bold mb-4">{companyInfo.name}</h3>
            <p className="text-sm mb-4">Empowering your digital future with intelligent, secure IT and telecommunication solutions.</p>
            <address className="not-italic text-sm text-gray-400">
              <p>{companyInfo.address}</p>
              <p className="mt-2">{companyInfo.phones[0]}</p>
              <p>{companyInfo.emails[0]}</p>
            </address>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/about" className="hover:text-white transition-colors">About Us</Link></li>
              <li><Link to="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              <li><Link to="/industries" className="hover:text-white transition-colors">Industries We Serve</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Solutions</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/solutions" className="hover:text-white transition-colors">All Solutions</Link></li>
              <li><Link to="/solutions/broadband" className="hover:text-white transition-colors">Broadband Connectivity</Link></li>
              <li><Link to="/solutions/security" className="hover:text-white transition-colors">Security Solutions</Link></li>
              <li><Link to="/solutions/smart-classroom" className="hover:text-white transition-colors">Smart Classroom</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="/assets/company-profile.pdf" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Download Company Profile</a></li>
              <li><Link to="/resources" className="hover:text-white transition-colors">View All Resources</Link></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-12 pt-8 text-sm text-center">
          <p>&copy; {new Date().getFullYear()} {companyInfo.name}. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
