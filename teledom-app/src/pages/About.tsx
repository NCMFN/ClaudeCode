import React from 'react';
import { Helmet } from 'react-helmet-async';
import { team, stats } from '../data';
import { motion } from 'framer-motion';

const About: React.FC = () => {
  return (
    <div className="pt-20">
      <Helmet>
        <title>Teledom Group - About Us</title>
        <meta name="description" content="Learn more about Teledom Group, our mission, and the leadership team driving IT and telecommunications innovation." />
      </Helmet>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-900 to-blue-800 text-white py-24 relative overflow-hidden">
        <div className="absolute inset-0 z-0 opacity-20">
          <img src="/assets/about.jpg" alt="About Teledom" className="w-full h-full object-cover" />
        </div>
        <div className="container mx-auto px-4 text-center relative z-10">
          <motion.h1
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-4xl md:text-5xl font-bold mb-6"
          >
            About Teledom Group
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl max-w-3xl mx-auto text-blue-100"
          >
            A legacy of excellence in delivering cutting-edge IT and telecommunications solutions that empower enterprises and government agencies worldwide.
          </motion.p>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <img
                src="/assets/datacenter.jpeg"
                alt="Teledom infrastructure"
                className="rounded-lg shadow-2xl"
              />
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h2 className="text-3xl font-bold mb-6 text-gray-900 border-l-4 border-blue-600 pl-4">Our Mission</h2>
              <p className="text-gray-600 mb-10 text-lg leading-relaxed">
                To bridge the digital divide by providing robust, innovative, and scalable IT and telecommunications infrastructure that drives business success and technological advancement across Nigeria and beyond.
              </p>

              <h2 className="text-3xl font-bold mb-6 text-gray-900 border-l-4 border-blue-600 pl-4">Our Vision</h2>
              <p className="text-gray-600 text-lg leading-relaxed">
                To be the globally recognized leader in intelligent digital solutions, setting the standard for reliability, security, and enterprise connectivity.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-blue-50 border-y border-blue-100">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                className="text-center bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <div className="text-2xl md:text-3xl font-bold text-blue-600 mb-2">{stat.value}</div>
                <div className="text-gray-600 font-semibold uppercase tracking-wide text-xs">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Leadership Spotlight */}
      <section id="ceo" className="py-24 bg-white relative">
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-gray-50 rounded-full opacity-50 blur-3xl"></div>
        </div>
        <div className="container mx-auto px-4 relative z-10">
          <h2 className="text-4xl font-bold text-center mb-16 text-gray-900">Meet Our CEO</h2>
          <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
            <div className="flex flex-col md:flex-row">
              <div className="md:w-2/5 h-80 md:h-auto relative">
                {/* Note: Ensure the image file is actually copied to this path */}
                <img
                  src={team[0].image}
                  alt={team[0].name}
                  className="w-full h-full object-cover object-top"
                  onError={(e) => {
                     (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x500?text=Dr.+Ekuwem';
                  }}
                />
              </div>
              <div className="md:w-3/5 p-8 md:p-12 flex flex-col justify-center">
                <h3 className="text-3xl font-bold text-gray-900 mb-2">{team[0].name}</h3>
                <p className="text-blue-600 font-semibold text-lg mb-6 uppercase tracking-wider">{team[0].role}</p>
                <p className="text-gray-600 leading-relaxed text-lg">
                  {team[0].bio}
                </p>
                <div className="mt-8">
                  <a href="/contact" className="inline-flex items-center font-semibold text-blue-600 hover:text-blue-800 transition-colors">
                    Get in touch <span className="ml-2">→</span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Our Work / Gallery Section */}
      <section className="py-20 bg-gray-900 text-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-4">Our Work in Action</h2>
          <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">Real installations, data center setups, and enterprise deployments across Nigeria.</p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="group relative overflow-hidden rounded-lg aspect-video bg-gray-800 cursor-pointer">
              <img src="/assets/broadband.png" alt="Broadband Setup" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <span className="text-white font-semibold text-lg">Broadband Connectivity</span>
              </div>
            </div>
            <div className="group relative overflow-hidden rounded-lg aspect-video bg-gray-800 cursor-pointer">
              <img src="/assets/security.jpg" alt="Security Setup" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <span className="text-white font-semibold text-lg">Military-Grade Security</span>
              </div>
            </div>
            <div className="group relative overflow-hidden rounded-lg aspect-video bg-gray-800 cursor-pointer">
              <img src="/assets/Smart-classroom.png" alt="Smart Classroom" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <span className="text-white font-semibold text-lg">Smart Classrooms</span>
              </div>
            </div>
            <div className="group relative overflow-hidden rounded-lg aspect-video bg-gray-800 cursor-pointer">
              <img src="/assets/datacenter.jpeg" alt="Data Center" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <span className="text-white font-semibold text-lg">Infrastructure</span>
              </div>
            </div>
            <div className="group relative overflow-hidden rounded-lg aspect-video bg-gray-800 cursor-pointer">
              <img src="/assets/smartId.jpeg" alt="Identity Systems" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <span className="text-white font-semibold text-lg">Identity & Tracking</span>
              </div>
            </div>
            <div className="group relative overflow-hidden rounded-lg aspect-video bg-gray-800 cursor-pointer">
              <img src="/assets/video.jpg" alt="Video Comm" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <span className="text-white font-semibold text-lg">Video Conferencing</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;
