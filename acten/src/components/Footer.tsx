import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-acten-charcoal text-acten-ivory py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-serif font-bold text-acten-gold mb-4">ACTEN</h3>
            <p className="text-sm">
              Association of Catholic Trained Evangelizers in Nigeria.<br/>
              Proclaiming Christ. Sharing the Gospel. Serving Communities.
            </p>
          </div>
          <div>
            <h4 className="text-lg font-bold mb-4">Navigation</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/about" className="hover:text-acten-gold">About Us</Link></li>
              <li><Link href="/news" className="hover:text-acten-gold">News</Link></li>
              <li><Link href="/events" className="hover:text-acten-gold">Events</Link></li>
              <li><Link href="/resources" className="hover:text-acten-gold">Resources</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-lg font-bold mb-4">Connect</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/contact" className="hover:text-acten-gold">Contact Us</Link></li>
              <li><Link href="/reports/submit" className="hover:text-acten-gold">Submit a Report</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-lg font-bold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/privacy" className="hover:text-acten-gold">Privacy Policy</Link></li>
              <li><Link href="/terms" className="hover:text-acten-gold">Terms of Use</Link></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 border-t border-gray-700 pt-8 text-center text-sm">
          <p>&copy; {2023} ACTEN. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
