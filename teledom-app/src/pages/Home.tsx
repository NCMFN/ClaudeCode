import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import LogoCarousel from '../components/LogoCarousel';
import { partners, solutions } from '../data';
import { motion } from 'framer-motion';
import { Play, Pause } from 'lucide-react';

const Home: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(true);

  return (
    <div className="pt-20">
      <Helmet>
        <title>Teledom Group - Intelligent Digital Solutions</title>
        <meta name="description" content="Welcome to Teledom Group, providing top IT, security, and telecommunication solutions across Nigeria." />
      </Helmet>

      {/* Hero Section with Video Placeholder */}
      <section className="relative bg-gray-900 text-white py-32 md:py-48 overflow-hidden">
        {/* Placeholder for real video footage. Currently using a static fallback. */}
        <div className="absolute inset-0 z-0">
          <div className="w-full h-full bg-blue-900 absolute inset-0 mix-blend-multiply opacity-50 z-10"></div>
          {/* Note: Requires actual B-Roll video footage before launch */}
          <video
            className={`w-full h-full object-cover ${isPlaying ? 'block' : 'hidden'}`}
            autoPlay
            loop
            muted
            playsInline
            poster="/assets/hero.png" // Static fallback
          >
             {/* <source src="/assets/hero-video.mp4" type="video/mp4" /> */}
          </video>
          {!isPlaying && (
            <img src="/assets/hero.png" alt="Hero fallback" className="w-full h-full object-cover" />
          )}
        </div>

        <div className="container mx-auto px-4 relative z-20 h-full flex flex-col justify-center">
          <div className="max-w-4xl">
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-5xl md:text-7xl font-bold mb-6 leading-tight drop-shadow-lg"
            >
              Empowering Your <span className="text-blue-400">Digital Future</span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-xl md:text-2xl mb-10 max-w-2xl text-gray-200 drop-shadow-md"
            >
              Innovative IT, Security, and Telecommunication solutions for enterprises and government agencies that demand excellence.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="space-x-4 flex items-center"
            >
              <Link to="/contact" className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-md font-semibold text-lg transition-all shadow-lg hover:shadow-blue-500/50">
                Request a Consultation
              </Link>

              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="flex items-center justify-center w-12 h-12 rounded-full bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/30 transition-colors"
                aria-label={isPlaying ? "Pause video" : "Play video"}
              >
                {isPlaying ? <Pause className="w-5 h-5 text-white" /> : <Play className="w-5 h-5 text-white ml-1" />}
              </button>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Solutions Teaser */}
      <section className="py-20 bg-gray-50 relative -mt-10 z-30 rounded-t-3xl">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Our Core Solutions</h2>
            <div className="w-24 h-1 bg-blue-600 mx-auto rounded-full"></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {solutions.slice(0,3).map((solution, idx) => (
              <motion.div
                key={solution.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow group"
              >
                <div className="h-48 overflow-hidden">
                   <img src={solution.image} alt={solution.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-3">{solution.title}</h3>
                  <p className="text-gray-600 mb-4 line-clamp-2">{solution.description}</p>
                  <Link to={`/solutions/${solution.id}`} className="text-blue-600 font-semibold flex items-center group-hover:text-blue-800 transition-colors">
                    Learn more <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
          <div className="text-center mt-12">
             <Link to="/solutions" className="inline-block border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white px-8 py-3 rounded-md font-semibold transition-colors">
                View All Solutions
             </Link>
          </div>
        </div>
      </section>

      {/* Partners Logo Carousel */}
      <section className="py-16 bg-white border-t border-gray-100">
        <div className="container mx-auto px-4">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Trusted by Government and Enterprise Clients Across Nigeria</h2>
            <p className="text-gray-500">Delivering reliable infrastructure to the nation's leading organizations.</p>
          </div>
          <LogoCarousel logos={partners} />
          {/* Note to client: Missing real logo assets for these partners. Falling back to styled text. */}
        </div>
      </section>
    </div>
  );
};

export default Home;
