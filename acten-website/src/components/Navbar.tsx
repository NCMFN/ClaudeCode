"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";

const mainNav = [
  { href: "/", label: "Home" },
  { href: "/about", label: "About ACTEN" },
  { href: "/news", label: "Evangelization News" },
  { href: "/events", label: "Activities & Events" },
  { href: "/resources", label: "Formation & Resources" },
  { href: "/gallery", label: "Gallery" },
  { href: "/reports", label: "Diocesan Reports" },
  { href: "/contact", label: "Contact" },
];

export const Navbar = () => {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Only set mounted after initial render to avoid hydration mismatch
    const timer = setTimeout(() => {
      setMounted(true);
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  return (
    <nav className="bg-acten-green text-acten-ivory sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          <div className="flex-shrink-0">
            <Link href="/" className="font-serif text-2xl font-bold tracking-tight text-acten-gold flex items-center gap-2">
              <span>ACTEN</span>
            </Link>
          </div>

          <div className="hidden lg:block">
            <div className="ml-10 flex items-center space-x-4">
              {mounted && mainNav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    pathname === item.href
                      ? "bg-acten-burgundy text-white"
                      : "hover:bg-acten-green-700 hover:text-acten-gold"
                  }`}
                >
                  {item.label}
                </Link>
              ))}

                <Link href="/admin" className="text-sm hover:text-acten-gold font-medium ml-4 pl-4 border-l border-acten-ivory/20">Admin</Link>
            </div>
          </div>

          <div className="lg:hidden flex items-center">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-acten-ivory hover:text-white hover:bg-acten-green-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
            >
              <span className="sr-only">Open main menu</span>
              {isOpen ? (
                <svg className="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="lg:hidden bg-acten-green-900 border-t border-acten-ivory/10">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            {mounted && mainNav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  pathname === item.href
                    ? "bg-acten-burgundy text-white"
                    : "hover:bg-acten-green-700 hover:text-acten-gold"
                }`}
                onClick={() => setIsOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <Link href="/admin" className="block px-3 py-2 rounded-md text-base font-medium hover:bg-acten-green-700 hover:text-acten-gold" onClick={() => setIsOpen(false)}>Admin</Link>
          </div>
        </div>
      )}
    </nav>
  );
};
