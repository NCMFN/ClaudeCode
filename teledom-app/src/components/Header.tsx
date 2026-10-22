import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { solutions, industries } from '../data';

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

  const navLinks = [
    {
      name: 'About Us',
      path: '/about',
      dropdown: [
        { name: 'Meet the CEO', path: '/about#team' },
        { name: 'Our Identity', path: '/about#identity' }
      ]
    },
    {
      name: 'Solutions',
      path: '/solutions',
      dropdown: solutions.map(sol => ({ name: sol.title, path: `/solutions/${sol.id}` }))
    },
    {
      name: 'Industries',
      path: '/industries',
      dropdown: industries.map(ind => ({ name: ind.title, path: `/industries#${ind.id}` }))
    },
  ];

  return (
    <header className={`fixed top-0 z-50 w-full transition-shadow duration-300 ${isScrolled ? 'bg-white shadow-md' : 'bg-white/90 backdrop-blur-md border-b border-gray-100'}`}>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          <div className="flex-shrink-0">
            <Link to="/" className="text-2xl font-bold text-blue-900 tracking-tight">Teledom International</Link>
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
                <Link to={link.path} className="flex items-center text-gray-700 hover:text-blue-600 font-medium py-2 transition-colors">
                  {link.name}
                  {link.dropdown && <ChevronDown className="ml-1 h-4 w-4" />}
                </Link>
                {link.dropdown && activeDropdown === link.name && (
                  <div className="absolute left-0 mt-2 w-56 rounded-md shadow-xl bg-white ring-1 ring-black ring-opacity-5 focus:outline-none overflow-hidden transform opacity-100 scale-100 transition duration-150 ease-out origin-top-left max-h-[70vh] overflow-y-auto">
                    <div className="py-1">
                      {link.dropdown.map((subLink) => (
                        <Link
                          key={subLink.name}
                          to={subLink.path}
                          className="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700 transition-colors"
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
            <Link to="/contact" className="bg-blue-600 text-white px-6 py-2.5 rounded-md font-medium hover:bg-blue-700 transition-colors shadow-sm hover:shadow focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
              Request a Consultation
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-gray-700 hover:text-blue-600 focus:outline-none p-2 rounded-md focus:ring-2 focus:ring-blue-500"
              aria-label="Toggle Menu"
              aria-expanded={mobileMenuOpen}
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
            className="md:hidden bg-white border-t border-gray-100 shadow-xl absolute w-full max-h-[80vh] overflow-y-auto"
          >
            <div className="px-4 pt-2 pb-6 space-y-1">
              {navLinks.map((link) => (
                <div key={link.name} className="py-2">
                  <Link
                    to={link.path}
                    className="block text-base font-semibold text-gray-900"
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
                  className="block w-full text-center bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 transition-colors shadow focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
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
