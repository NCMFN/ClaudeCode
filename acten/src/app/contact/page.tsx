import { Mail, MapPin, Phone } from 'lucide-react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Contact Us | ACTEN',
};

export default function ContactPage() {
  return (
    <div className="flex flex-col min-h-screen bg-brand-ivory">
      <div className="bg-brand-green py-12 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl font-serif text-white mb-2">Contact Us</h1>
          <p className="text-brand-gold text-lg">Get in touch with the ACTEN National Secretariat</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12 w-full grid grid-cols-1 md:grid-cols-2 gap-12">
        {/* Contact Info */}
        <div>
          <h2 className="text-2xl font-serif text-brand-green mb-6">Reach Out</h2>
          <p className="text-gray-600 mb-8 leading-relaxed">
            For general inquiries, media requests, or questions regarding report submissions, please use the contact form or reach us via the details below.
          </p>

          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-white border border-gray-200 rounded text-brand-gold">
                <MapPin size={24} />
              </div>
              <div>
                <h4 className="font-bold text-gray-800">Office Address</h4>
                <p className="text-sm text-gray-600 mt-1">Catholic Secretariat of Nigeria<br/>Abuja, Nigeria</p>
                <p className="text-xs text-gray-400 mt-1 italic">(Pending verified office location)</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="p-3 bg-white border border-gray-200 rounded text-brand-gold">
                <Mail size={24} />
              </div>
              <div>
                <h4 className="font-bold text-gray-800">Email Address</h4>
                <p className="text-sm text-gray-600 mt-1">info@acten.org.ng</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="p-3 bg-white border border-gray-200 rounded text-brand-gold">
                <Phone size={24} />
              </div>
              <div>
                <h4 className="font-bold text-gray-800">Telephone</h4>
                <p className="text-sm text-gray-600 mt-1">Available upon request</p>
              </div>
            </div>
          </div>
        </div>

        {/* Contact Form */}
        <div className="bg-white p-8 rounded-lg shadow-sm border border-brand-light-grey">
          <h2 className="text-2xl font-serif text-brand-green mb-6">Send a Message</h2>
          <form className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <input type="text" className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                <input type="text" className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
              <input type="email" className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
              <select className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none">
                <option>General Inquiry</option>
                <option>Report Submission Help</option>
                <option>Correction Request</option>
                <option>Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
              <textarea rows={4} className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none"></textarea>
            </div>
            <button type="button" className="w-full bg-brand-green text-white py-3 rounded font-medium hover:bg-opacity-90 transition-colors">
              Send Message
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
