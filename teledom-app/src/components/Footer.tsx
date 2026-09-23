import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-gray-300 py-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-white text-xl font-bold mb-4">Teledom</h3>
            <p className="text-sm">Providing robust IT and Telecommunication solutions across various industries.</p>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/about" className="hover:text-white transition-colors">About Us</Link></li>
              <li><Link to="/contact" className="hover:text-white transition-colors">Contact</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Solutions</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/solutions" className="hover:text-white transition-colors">All Solutions</Link></li>
              <li><Link to="/industries" className="hover:text-white transition-colors">Industries</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#pdf" className="hover:text-white transition-colors">Download Company Profile</a></li>
              <li><Link to="/resources" className="hover:text-white transition-colors">Blog & Insights</Link></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-12 pt-8 text-sm text-center">
          <p>&copy; {new Date().getFullYear()} Teledom. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
