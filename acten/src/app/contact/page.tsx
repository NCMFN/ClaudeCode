import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Contact Us | ACTEN',
  description: 'Get in touch with the Association of Catholic Trained Evangelizers in Nigeria.',
};

export default function ContactPage() {
  return (
    <div className="bg-white min-h-screen pb-16">
      <div className="bg-acten-charcoal py-16 text-center text-acten-ivory">
        <h1 className="text-4xl font-serif font-bold text-acten-gold mb-4">Contact Us</h1>
        <p className="text-lg max-w-2xl mx-auto">Get in touch or submit an evangelization report.</p>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          {/* Contact Information */}
          <div>
            <h2 className="text-2xl font-serif font-bold text-acten-green mb-6">Get In Touch</h2>
            <div className="space-y-6 text-gray-600">
              <div className="bg-acten-ivory p-6 rounded-lg border border-gray-100">
                <h3 className="font-bold text-acten-charcoal mb-2">Official Secretariat</h3>
                <p>Address details pending confirmation by ACTEN leadership.</p>
              </div>
              <div className="bg-acten-ivory p-6 rounded-lg border border-gray-100">
                <h3 className="font-bold text-acten-charcoal mb-2">Email & Phone</h3>
                <p>Contact details pending confirmation.</p>
              </div>
            </div>
          </div>

          {/* Contact Form */}
          <div className="bg-white p-8 rounded-lg shadow-lg border border-gray-100">
            <h2 className="text-2xl font-serif font-bold text-acten-burgundy mb-6">Send a Message</h2>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input type="text" className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-acten-green focus:border-acten-green bg-white" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <input type="email" className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-acten-green focus:border-acten-green bg-white" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                <select className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-acten-green focus:border-acten-green bg-white">
                  <option>General Enquiry</option>
                  <option>Submit a Report</option>
                  <option>Partnership</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
                <textarea rows={5} className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-acten-green focus:border-acten-green bg-white" required></textarea>
              </div>
              <button type="submit" className="w-full bg-acten-green text-white px-6 py-3 rounded-md font-bold hover:bg-opacity-90 transition-colors">
                Send Message
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
