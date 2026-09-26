import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import LogoCarousel from '../components/LogoCarousel';
import { partners, solutions } from '../data';
import { motion } from 'framer-motion';
import { ArrowRight, ChevronRight, CheckCircle2 } from 'lucide-react';

const Home: React.FC = () => {
  return (
    <div className="pt-20 bg-gray-50">
      <Helmet>
        <title>Teledom International - Empowering Your Digital Future</title>
        <meta name="description" content="Welcome to Teledom International, providing top IT, telecommunication, and security solutions in Nigeria." />
      </Helmet>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 text-white py-32 lg:py-48 overflow-hidden shadow-inner">
        {/* Real video hero placeholder overlay */}
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-blue-900 mix-blend-multiply opacity-80 z-10"></div>
          {/* Fallback image representing video */}
          <img src="https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&q=80" alt="Tech Background" className="w-full h-full object-cover opacity-40" />
        </div>

        <div className="container mx-auto px-4 relative z-20">
          <div className="max-w-4xl">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
              <span className="inline-block py-1 px-3 rounded-full bg-blue-800/50 border border-blue-400/30 text-blue-200 text-sm font-semibold tracking-wider mb-6 backdrop-blur-sm">
                LEADING IT SOLUTIONS IN NIGERIA
              </span>
              <h1 className="text-5xl md:text-7xl font-extrabold mb-6 drop-shadow-xl tracking-tight leading-tight">
                Empowering Your <br className="hidden md:block"/>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">Digital Future</span>
              </h1>
              <p className="text-xl md:text-2xl mb-10 text-blue-50 drop-shadow max-w-2xl font-light leading-relaxed">
                Innovative IT, Telecommunication, and Security solutions for enterprises and government agencies that demand excellence.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/contact" className="inline-flex justify-center items-center bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all shadow-[0_0_20px_rgba(37,99,235,0.4)] hover:shadow-[0_0_30px_rgba(37,99,235,0.6)] hover:-translate-y-1">
                  Get Started
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Link>
                <Link to="/solutions" className="inline-flex justify-center items-center bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all shadow-lg hover:shadow-xl hover:-translate-y-1">
                  Explore Solutions
                </Link>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Partners Logo Carousel */}
      <section className="py-12 bg-white border-b border-gray-100 shadow-[0_4px_20px_-10px_rgba(0,0,0,0.05)] relative z-20">
        <div className="container mx-auto px-4">
          <p className="text-center text-sm font-bold text-gray-400 uppercase tracking-widest mb-8">Trusted by Government & Enterprise Clients</p>
          <LogoCarousel logos={partners} />
        </div>
      </section>

      {/* Featured Solutions */}
      <section className="py-24 bg-gray-50 relative">
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-30 pointer-events-none"></div>
          <div className="container mx-auto px-4 relative z-10">
              <div className="text-center max-w-3xl mx-auto mb-16">
                <h2 className="text-4xl font-extrabold mb-4 text-gray-900 tracking-tight">Enterprise Solutions</h2>
                <p className="text-xl text-gray-600">Discover our comprehensive suite of advanced technology, security, and connectivity services.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {solutions.slice(0, 6).map((sol, index) => (
                  <motion.div
                    key={sol.id}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-white rounded-2xl p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_20px_40px_rgb(0,0,0,0.08)] transition-all duration-300 border border-gray-100 group flex flex-col h-full"
                  >
                    <div className="w-14 h-14 bg-gradient-to-br from-blue-100 to-indigo-50 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-inner">
                       {/* Placeholder icon approach depending on ID */}
                       <div className="text-blue-600 font-bold text-xl">{sol.title.charAt(0)}</div>
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-3">{sol.title}</h3>
                    <p className="text-gray-600 mb-8 flex-grow">{sol.description}</p>
                    <Link to={`/solutions/${sol.id}`} className="inline-flex items-center text-blue-600 font-semibold group-hover:text-blue-800 transition-colors mt-auto">
                      Learn more
                      <ChevronRight className="ml-1 w-5 h-5 transform group-hover:translate-x-1 transition-transform" />
                    </Link>
                  </motion.div>
                ))}
              </div>

              <div className="mt-16 text-center">
                <Link to="/solutions" className="inline-flex justify-center items-center bg-white border-2 border-gray-200 hover:border-blue-600 text-gray-800 hover:text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg transition-all shadow-sm hover:shadow-md">
                    View All Solutions
                    <ArrowRight className="ml-2 w-5 h-5" />
                </Link>
              </div>
          </div>
      </section>

      {/* Why Choose Us Section */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="flex flex-col lg:flex-row items-center gap-16">
            <div className="lg:w-1/2">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl group">
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent z-10"></div>
                <img src="https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&q=80&w=800" alt="Teledom Office" className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700" />
                <div className="absolute bottom-6 left-6 z-20">
                  <p className="text-white font-bold text-2xl drop-shadow-md">Excellence Delivered.</p>
                </div>
              </div>
            </div>
            <div className="lg:w-1/2 space-y-8">
              <div>
                <h2 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-4">Why Teledom International?</h2>
                <p className="text-lg text-gray-600 leading-relaxed">
                  With decades of experience traversing the Nigerian tech landscape, we deliver unparalleled expertise, robust infrastructure, and dedicated support to fuel your business transformation.
                </p>
              </div>

              <ul className="space-y-4">
                {[
                  'Proven track record with top government and enterprise clients',
                  'Comprehensive, end-to-end IT and security solutions',
                  'Nationwide coverage and robust support infrastructure',
                  'Leadership by renowned industry experts'
                ].map((item, i) => (
                  <li key={i} className="flex items-start">
                    <CheckCircle2 className="text-blue-600 w-6 h-6 mr-3 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 font-medium text-lg">{item}</span>
                  </li>
                ))}
              </ul>

              <div>
                <Link to="/about" className="inline-flex items-center text-blue-600 font-semibold text-lg hover:text-blue-800 transition-colors">
                  Learn more about our company <ArrowRight className="ml-2 w-5 h-5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
