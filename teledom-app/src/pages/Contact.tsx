import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { Mail, Phone, MapPin, Send, CheckCircle } from 'lucide-react';
import { companyInfo } from '../data';
import { motion } from 'framer-motion';

const Contact: React.FC = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [formData, setFormData] = useState({
     name: '',
     email: '',
     subject: '',
     message: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
     setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate backend form submission (e.g. to a serverless function, Formspree, or custom API)
    // Needs real backend endpoint before launch. Note added for client.
    setTimeout(() => {
      setIsSubmitting(false);
      setIsSuccess(true);
      setFormData({ name: '', email: '', subject: '', message: '' });

      // Reset success state after a few seconds
      setTimeout(() => setIsSuccess(false), 5000);
    }, 1500);
  };

  return (
    <div className="pt-20">
      <Helmet>
        <title>Teledom Group - Contact Us</title>
        <meta name="description" content={`Contact Teledom Group at ${companyInfo.phones[0]} or visit our Lagos office.`} />
      </Helmet>

      {/* Page Header */}
      <section className="bg-blue-900 py-20 text-white relative overflow-hidden">
        <div className="absolute inset-0 z-0 opacity-20">
          <img src="/assets/contact-images.png" alt="Contact Us" className="w-full h-full object-cover" />
        </div>
        <div className="container mx-auto px-4 text-center relative z-10">
          <motion.h1
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-5xl font-bold mb-4"
          >
            Get in Touch
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xl text-blue-100 max-w-2xl mx-auto"
          >
            Our expert engineers and consultants are ready to help you design the perfect IT and telecommunications infrastructure.
          </motion.p>
        </div>
      </section>

      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="grid md:grid-cols-2 gap-12">

            {/* Contact Information */}
            <motion.div
               initial={{ opacity: 0, x: -30 }}
               animate={{ opacity: 1, x: 0 }}
               transition={{ duration: 0.5 }}
               className="space-y-8"
            >
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-6">Contact Information</h2>
                <p className="text-gray-600 mb-8 leading-relaxed">
                  Whether you need a consultation, support for an existing installation, or want to explore our solutions, we're here to help.
                </p>
              </div>

              <div className="space-y-6">
                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-blue-100 p-3 rounded-full text-blue-600 mt-1">
                    <MapPin className="h-6 w-6" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-gray-900">Head Office</h3>
                    <p className="text-gray-600 mt-1 leading-relaxed max-w-xs">{companyInfo.address}</p>
                  </div>
                </div>

                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-blue-100 p-3 rounded-full text-blue-600 mt-1">
                    <Phone className="h-6 w-6" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-gray-900">Phone</h3>
                    <div className="text-gray-600 mt-1 space-y-1">
                       {companyInfo.phones.map((phone, idx) => (
                          <p key={idx}>{phone}</p>
                       ))}
                    </div>
                  </div>
                </div>

                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-blue-100 p-3 rounded-full text-blue-600 mt-1">
                    <Mail className="h-6 w-6" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-gray-900">Email</h3>
                    <div className="text-gray-600 mt-1 space-y-1">
                       {companyInfo.emails.map((email, idx) => (
                          <p key={idx}><a href={`mailto:${email}`} className="hover:text-blue-600 transition-colors">{email}</a></p>
                       ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Map Placeholder */}
              <div className="w-full h-64 bg-gray-200 rounded-lg overflow-hidden border border-gray-300 relative shadow-inner">
                 {/* This should be replaced with an actual Google Maps iframe using the address */}
                 <div className="absolute inset-0 flex items-center justify-center flex-col text-gray-500 bg-gray-100">
                    <MapPin className="w-8 h-8 mb-2 opacity-50" />
                    <p className="font-medium text-center px-4">{companyInfo.address}</p>
                    <p className="text-xs mt-2">(Interactive Map Placeholder)</p>
                 </div>
              </div>
            </motion.div>

            {/* Contact Form */}
            <motion.div
               initial={{ opacity: 0, x: 30 }}
               animate={{ opacity: 1, x: 0 }}
               transition={{ duration: 0.5, delay: 0.2 }}
            >
              <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-100 relative">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">Send us a Message</h3>

                {/* Note for developer regarding backend */}
                <div className="text-xs text-amber-700 bg-amber-50 p-2 rounded mb-6 border border-amber-100">
                   Note: Form requires backend integration (e.g., Formspree, API route) to send real emails to {companyInfo.emails[0]}.
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                    <input
                      type="text"
                      id="name"
                      required
                      value={formData.name}
                      onChange={handleChange}
                      className="w-full px-4 py-3 rounded-md border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-colors"
                      placeholder="John Doe"
                    />
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email Address *</label>
                    <input
                      type="email"
                      id="email"
                      required
                      value={formData.email}
                      onChange={handleChange}
                      className="w-full px-4 py-3 rounded-md border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-colors"
                      placeholder="john@company.com"
                    />
                  </div>

                  <div>
                    <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                    <select
                      id="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      className="w-full px-4 py-3 rounded-md border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-colors bg-white"
                    >
                      <option value="">Select an inquiry type</option>
                      <option value="Sales & Solutions">Sales & Solutions</option>
                      <option value="Technical Support">Technical Support</option>
                      <option value="Partnership">Partnership</option>
                      <option value="General Inquiry">General Inquiry</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">Message *</label>
                    <textarea
                      id="message"
                      rows={5}
                      required
                      value={formData.message}
                      onChange={handleChange}
                      className="w-full px-4 py-3 rounded-md border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-colors resize-none"
                      placeholder="How can we help you?"
                    ></textarea>
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className={`w-full py-4 px-6 rounded-md font-semibold text-white transition-all flex justify-center items-center ${
                       isSuccess ? 'bg-green-600' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-lg'
                    } disabled:opacity-70 disabled:cursor-not-allowed`}
                  >
                    {isSubmitting ? (
                       <span className="flex items-center">
                          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Sending...
                       </span>
                    ) : isSuccess ? (
                       <span className="flex items-center">
                          <CheckCircle className="mr-2 h-5 w-5" /> Message Sent
                       </span>
                    ) : (
                       <span className="flex items-center">
                          <Send className="mr-2 h-5 w-5" /> Send Message
                       </span>
                    )}
                  </button>
                </form>
              </div>
            </motion.div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Contact;
