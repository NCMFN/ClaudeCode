import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const navLinks = [
  { name: 'About Us', path: '/about', dropdown: [{ name: 'Our Team', path: '/about#team' }, { name: 'Careers', path: '/about#careers' }] },
  { name: 'Solutions', path: '/solutions', dropdown: [{ name: 'Networking', path: '/solutions/networking' }, { name: 'Security', path: '/solutions/security' }] },
  { name: 'Industries', path: '/industries', dropdown: [{ name: 'Finance', path: '/industries#finance' }, { name: 'Healthcare', path: '/industries#healthcare' }] },
  { name: 'Resources', path: '/resources', dropdown: [{ name: 'Blog', path: '/resources#blog' }, { name: 'Whitepapers', path: '/resources#whitepapers' }] },
];

const Header: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={`fixed top-0 z-50 w-full transition-shadow duration-300 ${isScrolled ? 'bg-white shadow-md' : 'bg-white/90 backdrop-blur-md'}`}>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          <div className="flex-shrink-0">
            <Link to="/" className="text-2xl font-bold text-blue-900">Teledom</Link>
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex space-x-8">
            {navLinks.map((link) => (
              <div
                key={link.name}
                className="relative group"
                onMouseEnter={() => setActiveDropdown(link.name)} onFocus={() => setActiveDropdown(link.name)}
                onMouseLeave={() => setActiveDropdown(null)} onBlur={() => setActiveDropdown(null)}
              >
                <Link to={link.path} className="flex items-center text-gray-700 hover:text-blue-600 font-medium py-2">
                  {link.name}
                  {link.dropdown && <ChevronDown className="ml-1 h-4 w-4" />}
                </Link>
                {link.dropdown && activeDropdown === link.name && (
                  <div className="absolute left-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none">
                    <div className="py-1">
                      {link.dropdown.map((subLink) => (
                        <Link
                          key={subLink.name}
                          to={subLink.path}
                          className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          {subLink.name}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </nav>

          <div className="hidden md:flex items-center">
            <Link to="/contact" className="bg-blue-600 text-white px-6 py-2 rounded-md font-medium hover:bg-blue-700 transition-colors">
              Request a Consultation
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-gray-700 hover:text-blue-600 focus:outline-none"
              aria-label="Toggle Menu"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Nav */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-white border-t border-gray-200"
          >
            <div className="px-4 pt-2 pb-6 space-y-1">
              {navLinks.map((link) => (
                <div key={link.name} className="py-2">
                  <Link
                    to={link.path}
                    className="block text-base font-medium text-gray-900"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {link.name}
                  </Link>
                  {link.dropdown && (
                    <div className="pl-4 mt-2 space-y-2 border-l-2 border-gray-100">
                      {link.dropdown.map((subLink) => (
                        <Link
                          key={subLink.name}
                          to={subLink.path}
                          className="block text-sm font-medium text-gray-600 hover:text-blue-600"
                          onClick={() => setMobileMenuOpen(false)}
                        >
                          {subLink.name}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              <div className="pt-4">
                <Link
                  to="/contact"
                  className="block w-full text-center bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Request a Consultation
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};

export default Header;
