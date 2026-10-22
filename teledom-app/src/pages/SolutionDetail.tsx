import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import { solutions } from '../data';
import { motion, AnimatePresence } from 'framer-motion';

const SolutionDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const solution = solutions.find(s => s.id === id);
  const [activeTab, setActiveTab] = useState<'overview' | 'features' | 'benefits'>('overview');

  if (!solution) {
    return (
      <div className="pt-32 text-center text-2xl h-screen flex items-center justify-center">
        <div>
          <h2>Solution not found</h2>
          <Link to="/solutions" className="text-blue-600 underline mt-4 inline-block">Return to Solutions</Link>
        </div>
      </div>
    );
  }

  const tabContent = {
    overview: (
      <div className="space-y-4">
        <h3 className="text-2xl font-semibold text-gray-900">Overview</h3>
        <p className="text-gray-700 leading-relaxed text-lg">
          {solution.description} Discover how our specialized {solution.title} can streamline your operations, enhance security, and drive organizational growth.
        </p>
      </div>
    ),
    features: (
      <div className="space-y-4">
        <h3 className="text-2xl font-semibold text-gray-900">Key Capabilities</h3>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            'Scalable architecture tailored to enterprise demands.',
            'Continuous monitoring and expert engineering support.',
            'Seamless integration with existing legacy systems.',
            'Compliance with national security and data standards.',
            'High-availability design for zero-downtime operations.'
          ].map((feature, i) => (
             <li key={i} className="flex items-start">
                <span className="text-blue-600 mr-2 mt-1">✓</span>
                <span className="text-gray-700">{feature}</span>
             </li>
          ))}
        </ul>
      </div>
    ),
    benefits: (
      <div className="space-y-4">
        <h3 className="text-2xl font-semibold text-gray-900">Business Benefits</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
           <div className="bg-blue-50 p-6 rounded-lg border border-blue-100">
              <h4 className="font-bold text-blue-900 mb-2">Cost Efficiency</h4>
              <p className="text-sm text-gray-700">Optimize operational expenditure through intelligent infrastructure design.</p>
           </div>
           <div className="bg-blue-50 p-6 rounded-lg border border-blue-100">
              <h4 className="font-bold text-blue-900 mb-2">Enhanced Security</h4>
              <p className="text-sm text-gray-700">Mitigate risks with enterprise-grade protection and compliance standards.</p>
           </div>
           <div className="bg-blue-50 p-6 rounded-lg border border-blue-100">
              <h4 className="font-bold text-blue-900 mb-2">Future-Ready</h4>
              <p className="text-sm text-gray-700">Built to scale seamlessly as your organizational needs evolve.</p>
           </div>
        </div>
      </div>
    )
  };

  return (
    <div className="pt-20">
      <Helmet>
        <title>{`Teledom Group - ${solution.title}`}</title>
        <meta name="description" content={solution.description} />
      </Helmet>

      {/* Hero */}
      <section className="bg-gray-900 text-white relative py-24 md:py-32 overflow-hidden border-b-4 border-blue-600">
        <div className="absolute inset-0 z-0 opacity-30 mix-blend-overlay">
          {/* Use specific real image for the solution */}
          <img src={solution.image} alt={solution.title} className="w-full h-full object-cover" />
        </div>
        <div className="absolute inset-0 z-0 bg-gradient-to-r from-gray-900 via-gray-900/80 to-transparent"></div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-4xl md:text-5xl font-bold mb-6 leading-tight"
            >
              {solution.title}
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-xl text-gray-200 mb-10"
            >
              {solution.description}
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="space-x-4 flex items-center"
            >
              <Link to="/contact" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-md font-medium hover:bg-blue-500 transition-colors shadow-lg hover:shadow-blue-500/50">
                Request a Consultation
              </Link>
              {solution.brochure && (
                <a href={solution.brochure} target="_blank" rel="noopener noreferrer" className="inline-block bg-white/10 backdrop-blur-sm text-white border border-white/30 px-8 py-3 rounded-md font-medium hover:bg-white/20 transition-colors">
                  Download Brochure
                </a>
              )}
            </motion.div>
          </div>
        </div>
      </section>

      {/* Visual Showcase Feature (if applicable) */}
      <section className="py-12 bg-white -mt-10 relative z-20">
         <div className="container mx-auto px-4">
            <div className="max-w-5xl mx-auto rounded-xl overflow-hidden shadow-2xl border border-gray-100 h-[400px]">
               <img src={solution.image} alt={`${solution.title} Implementation`} className="w-full h-full object-cover" />
            </div>
         </div>
      </section>

      {/* Interactive Tabs */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4 max-w-5xl">
          <div className="flex border-b border-gray-200 mb-10 overflow-x-auto no-scrollbar">
            {(['overview', 'features', 'benefits'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-8 font-semibold text-sm sm:text-base whitespace-nowrap transition-all duration-300 ${
                  activeTab === tab
                    ? 'border-b-4 border-blue-600 text-blue-700 bg-blue-50/50'
                    : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'
                }`}
                aria-selected={activeTab === tab}
                role="tab"
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          <div className="min-h-[200px] p-4">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -15 }}
                transition={{ duration: 0.3 }}
                role="tabpanel"
              >
                {tabContent[activeTab]}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </section>
    </div>
  );
};

export default SolutionDetail;
