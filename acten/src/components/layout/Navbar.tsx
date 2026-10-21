import Link from 'next/link';
import { Menu, Search } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="bg-brand-green text-white py-4 px-6 md:px-12 sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto flex justify-between items-center">

        <Link href="/" className="flex items-center gap-2">
          <div className="text-brand-gold text-2xl font-serif">✝</div>
          <div className="flex flex-col">
            <span className="font-serif font-bold text-xl leading-none">ACTEN</span>
            <span className="text-[0.65rem] uppercase tracking-wider text-gray-200">
              Association of Catholic<br/>Trained Evangelizers in Nigeria
            </span>
          </div>
        </Link>

        <div className="hidden md:flex items-center gap-6 text-sm font-medium">
          <Link href="/" className="hover:text-brand-gold transition">Home</Link>
          <Link href="/about" className="hover:text-brand-gold transition">About ACTEN</Link>
          <Link href="/news" className="hover:text-brand-gold transition">News</Link>
          <Link href="/events" className="hover:text-brand-gold transition">Activities & Events</Link>
          <Link href="/resources" className="hover:text-brand-gold transition">Resources</Link>
          <Link href="/gallery" className="hover:text-brand-gold transition">Gallery</Link>
          <Link href="/reports" className="hover:text-brand-gold transition">Reports</Link>
          <Link href="/contact" className="hover:text-brand-gold transition">Contact</Link>

          <Link href="/submit" className="bg-brand-gold text-brand-green px-4 py-2 rounded-sm hover:bg-white transition ml-2">
            Submit Report
          </Link>
        </div>

        <div className="flex items-center gap-4">
          <button className="text-white hover:text-brand-gold">
            <Search size={20} />
          </button>
          <button className="md:hidden text-white hover:text-brand-gold">
            <Menu size={24} />
          </button>
        </div>
      </div>
    </nav>
  );
}
