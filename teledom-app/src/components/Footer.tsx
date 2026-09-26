import React from 'react';
import { Link } from 'react-router-dom';
import { companyInfo, solutions, industries } from '../data';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-gray-300 py-16 relative overflow-hidden">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          <div>
            <h3 className="text-white text-2xl font-bold mb-4 tracking-tight">{companyInfo.name}</h3>
            <p className="text-sm leading-relaxed mb-6">Providing robust IT, telecommunication, and security solutions across Nigeria.</p>
            <div className="text-sm space-y-2 text-gray-400">
              <p>{companyInfo.address}</p>
              <p>{companyInfo.phones[0]}</p>
              <p>{companyInfo.emails[0]}</p>
            </div>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4 text-lg">Company</h4>
            <ul className="space-y-3 text-sm">
              <li><Link to="/about" className="hover:text-blue-400 transition-colors">About Us</Link></li>
              <li><Link to="/about#team" className="hover:text-blue-400 transition-colors">Meet the CEO</Link></li>
              <li><Link to="/contact" className="hover:text-blue-400 transition-colors">Contact Us</Link></li>
              <li><a href="#" className="hover:text-blue-400 transition-colors">Download Company Profile</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4 text-lg">Solutions</h4>
            <ul className="space-y-3 text-sm">
              {solutions.slice(0, 5).map(sol => (
                <li key={sol.id}>
                  <Link to={`/solutions/${sol.id}`} className="hover:text-blue-400 transition-colors">
                    {sol.title}
                  </Link>
                </li>
              ))}
              <li><Link to="/solutions" className="hover:text-blue-400 transition-colors">All Solutions &rarr;</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4 text-lg">Industries</h4>
            <ul className="space-y-3 text-sm">
              {industries.slice(0, 5).map(ind => (
                <li key={ind.id}>
                  <Link to={`/industries#${ind.id}`} className="hover:text-blue-400 transition-colors">
                    {ind.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-16 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-gray-500">
          <p>&copy; {new Date().getFullYear()} {companyInfo.name}. All rights reserved.</p>
          <div className="mt-4 md:mt-0 space-x-6">
            <Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
