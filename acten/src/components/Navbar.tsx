import Link from 'next/link';

export default function Navbar() {
  return (
    <header className="bg-acten-green text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex-shrink-0">
            <Link href="/" className="text-2xl font-serif font-bold text-acten-gold">
              ACTEN
            </Link>
          </div>
          <nav className="hidden md:flex space-x-8">
            <Link href="/" className="hover:text-acten-gold px-3 py-2 rounded-md text-sm font-medium">Home</Link>
            <Link href="/about" className="hover:text-acten-gold px-3 py-2 rounded-md text-sm font-medium">About ACTEN</Link>
            <Link href="/news" className="hover:text-acten-gold px-3 py-2 rounded-md text-sm font-medium">News</Link>
            <Link href="/events" className="hover:text-acten-gold px-3 py-2 rounded-md text-sm font-medium">Events</Link>
            <Link href="/resources" className="hover:text-acten-gold px-3 py-2 rounded-md text-sm font-medium">Resources</Link>
            <Link href="/gallery" className="hover:text-acten-gold px-3 py-2 rounded-md text-sm font-medium">Gallery</Link>
            <Link href="/reports" className="hover:text-acten-gold px-3 py-2 rounded-md text-sm font-medium">Reports</Link>
            <Link href="/contact" className="hover:text-acten-gold px-3 py-2 rounded-md text-sm font-medium">Contact</Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
