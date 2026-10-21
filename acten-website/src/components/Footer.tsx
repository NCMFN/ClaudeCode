import Link from "next/link";

export const Footer = () => {
  return (
    <footer className="bg-acten-charcoal text-acten-ivory py-12 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-1">
            <h2 className="font-serif text-2xl font-bold text-acten-gold mb-4">ACTEN</h2>
            <p className="text-sm opacity-80 leading-relaxed mb-4">
              Association of Catholic Trained Evangelizers in Nigeria.
            </p>
            <p className="text-sm opacity-80 leading-relaxed">
              Proclaiming Christ.<br/>
              Sharing the Gospel.<br/>
              Serving Communities.
            </p>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-4 border-b border-acten-ivory/20 pb-2">Quick Links</h3>
            <ul className="space-y-2">
              <li><Link href="/about" className="text-sm opacity-80 hover:opacity-100 hover:text-acten-gold transition-colors">About ACTEN</Link></li>
              <li><Link href="/news" className="text-sm opacity-80 hover:opacity-100 hover:text-acten-gold transition-colors">News</Link></li>
              <li><Link href="/events" className="text-sm opacity-80 hover:opacity-100 hover:text-acten-gold transition-colors">Events</Link></li>
              <li><Link href="/resources" className="text-sm opacity-80 hover:opacity-100 hover:text-acten-gold transition-colors">Resources</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-4 border-b border-acten-ivory/20 pb-2">Connect</h3>
            <ul className="space-y-2">
              <li><Link href="/reports" className="text-sm opacity-80 hover:opacity-100 hover:text-acten-gold transition-colors">Submit a Report</Link></li>
              <li><Link href="/contact" className="text-sm opacity-80 hover:opacity-100 hover:text-acten-gold transition-colors">Contact Us</Link></li>
              <li><Link href="/gallery" className="text-sm opacity-80 hover:opacity-100 hover:text-acten-gold transition-colors">Gallery</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-4 border-b border-acten-ivory/20 pb-2">Contact</h3>
            <address className="not-italic text-sm opacity-80 space-y-2">
              <p>Catholic Secretariat of Nigeria</p>
              <p>Abuja, Nigeria</p>
              <p className="mt-4"><a href="mailto:info@acten.ng" className="hover:text-acten-gold transition-colors">info@acten.ng</a></p>
            </address>
          </div>
        </div>

        <div className="border-t border-acten-ivory/20 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center text-xs opacity-60">
          <p>&copy; 2026 ACTEN. All rights reserved.</p>
          <div className="flex space-x-4 mt-4 md:mt-0">
            <Link href="/privacy" className="hover:text-acten-gold transition-colors">Privacy Policy</Link>
            <Link href="/terms" className="hover:text-acten-gold transition-colors">Terms of Use</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};
