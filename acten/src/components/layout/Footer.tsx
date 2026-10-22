import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-brand-charcoal text-white pt-12 pb-6 px-6 md:px-12">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">

        <div className="col-span-1 md:col-span-1">
          <h3 className="font-serif text-xl text-brand-gold mb-4 flex items-center gap-2">
            <span>✝</span> ACTEN
          </h3>
          <p className="text-sm text-gray-300 mb-4">
            Association of Catholic Trained Evangelizers in Nigeria.
            Proclaiming Christ. Sharing the Gospel. Serving Communities.
          </p>
        </div>

        <div>
          <h4 className="font-bold mb-4 uppercase text-sm tracking-wider text-gray-400">Quick Links</h4>
          <ul className="space-y-2 text-sm">
            <li><Link href="/about" className="hover:text-brand-gold transition">About Us</Link></li>
            <li><Link href="/news" className="hover:text-brand-gold transition">Evangelization News</Link></li>
            <li><Link href="/events" className="hover:text-brand-gold transition">Upcoming Events</Link></li>
            <li><Link href="/resources" className="hover:text-brand-gold transition">Formation Resources</Link></li>
            <li><Link href="/reports" className="hover:text-brand-gold transition">Diocesan Reports</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold mb-4 uppercase text-sm tracking-wider text-gray-400">Information</h4>
          <ul className="space-y-2 text-sm">
            <li><Link href="/contact" className="hover:text-brand-gold transition">Contact Us</Link></li>
            <li><Link href="/submit" className="hover:text-brand-gold transition">Submit a Report</Link></li>
            <li><Link href="#" className="hover:text-brand-gold transition">Privacy Policy</Link></li>
            <li><Link href="#" className="hover:text-brand-gold transition">Terms of Use</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold mb-4 uppercase text-sm tracking-wider text-gray-400">Contact</h4>
          <address className="not-italic text-sm text-gray-300 space-y-2">
            <p>Catholic Secretariat of Nigeria</p>
            <p>Abuja, Nigeria</p>
            <p className="mt-4"><a href="mailto:info@acten.org.ng" className="hover:text-brand-gold transition">info@acten.org.ng</a></p>
          </address>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-6 border-t border-gray-700 text-sm text-center text-gray-400 flex flex-col md:flex-row justify-between items-center">
        <p>&copy; 2026 ACTEN. All rights reserved.</p>
        <p className="mt-2 md:mt-0 text-xs">For technical issues or corrections, please <Link href="/contact" className="underline hover:text-white">contact the webmaster</Link>.</p>
      </div>
    </footer>
  );
}
