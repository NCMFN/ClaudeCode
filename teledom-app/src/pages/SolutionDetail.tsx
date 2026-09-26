import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { solutions } from '../data';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, ArrowRight } from 'lucide-react';

const SolutionDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const solution = solutions.find(s => s.id === id);
  const [activeTab, setActiveTab] = useState<'overview' | 'features' | 'benefits'>('overview');

  if (!solution) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Solution not found</h2>
          <Link to="/solutions" className="text-blue-600 hover:underline">Return to all solutions</Link>
        </div>
      </div>
    );
  }

  // Choose a relevant placeholder image based on the solution ID, otherwise generic
  const getImageForSolution = (solutionId: string) => {
    const placeholders: Record<string, string> = {
      'broadband': 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&q=80&w=1200', // fiber/cabling
      'identity-capture': 'https://images.unsplash.com/photo-1581092334651-ddf26d9a09d0?auto=format&fit=crop&q=80&w=1200', // biometrics/tech
      'security': 'https://images.unsplash.com/photo-1557597774-9d273605dfa9?auto=format&fit=crop&q=80&w=1200', // CCTV/Security
      'smart-classroom': 'https://images.unsplash.com/photo-1577896851231-70ef18881754?auto=format&fit=crop&q=80&w=1200', // Classroom screen
    };
    return placeholders[solutionId] || 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=1200'; // generic tech
  };

  const tabContent = {
    overview: (
      <div className="space-y-6">
        <h3 className="text-2xl font-bold text-gray-900">Overview</h3>
        <p className="text-gray-700 text-lg leading-relaxed">
          {solution.description}
        </p>
        <p className="text-gray-700 text-lg leading-relaxed">
          At Teledom International, we understand that robust {solution.title.toLowerCase()} is critical to modern enterprise success. Our specialized approach ensures high availability, scalability, and seamless integration with your existing infrastructure.
        </p>
      </div>
    ),
    features: (
      <div className="space-y-6">
        <h3 className="text-2xl font-bold text-gray-900">Key Features</h3>
        <ul className="space-y-4">
          {[
            'Scalable architecture tailored precisely to your operational needs.',
            'Comprehensive 24/7 monitoring and proactive technical support.',
            'Seamless integration capabilities with legacy and modern systems.',
            'Built-in redundancy and failover mechanisms for high availability.',
            'Advanced analytics and reporting for operational visibility.'
          ].map((feature, i) => (
            <li key={i} className="flex items-start bg-white p-4 rounded-lg shadow-sm border border-gray-50">
              <CheckCircle2 className="text-blue-600 w-6 h-6 mr-3 flex-shrink-0" />
              <span className="text-gray-700">{feature}</span>
            </li>
          ))}
        </ul>
      </div>
    ),
    benefits: (
      <div className="space-y-6">
        <h3 className="text-2xl font-bold text-gray-900">Business Benefits</h3>
        <div className="grid sm:grid-cols-2 gap-4">
          {[
            { title: 'Cost Efficiency', desc: 'Significantly reduce long-term operational expenditures.' },
            { title: 'Enhanced Security', desc: 'Protect critical assets with state-of-the-art compliance protocols.' },
            { title: 'Improved Performance', desc: 'Boost overall system reliability and speed.' },
            { title: 'Future-Proof', desc: 'Ready your business for tomorrow\'s technological demands.' }
          ].map((benefit, i) => (
            <div key={i} className="bg-blue-50/50 p-6 rounded-xl border border-blue-100">
              <h4 className="font-bold text-blue-900 mb-2">{benefit.title}</h4>
              <p className="text-sm text-gray-600">{benefit.desc}</p>
            </div>
          ))}
        </div>
      </div>
    )
  };

  return (
    <div className="pt-20 bg-gray-50 min-h-screen">
      <Helmet>
        <title>{`Teledom - ${solution.title}`}</title>
        <meta name="description" content={solution.description} />
      </Helmet>

      {/* Hero Section with Image Background and Gradients */}
      <section className="relative py-24 lg:py-32 overflow-hidden bg-gray-900">
        <div className="absolute inset-0 z-0">
          <img src={getImageForSolution(solution.id)} alt={solution.title} className="w-full h-full object-cover opacity-40 mix-blend-overlay" />
          <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/80 to-transparent"></div>
        </div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl">
            <Link to="/solutions" className="inline-flex items-center text-blue-400 hover:text-blue-300 mb-6 transition-colors text-sm font-semibold tracking-wide uppercase">
              <ArrowRight className="w-4 h-4 mr-2 rotate-180" /> Back to Solutions
            </Link>
            <h1 className="text-4xl md:text-6xl font-extrabold text-white mb-6 drop-shadow-lg tracking-tight">{solution.title}</h1>
            <p className="text-xl text-gray-300 mb-10 max-w-2xl leading-relaxed drop-shadow">{solution.description}</p>
            <div className="flex flex-wrap gap-4">
              <Link to="/contact" className="inline-flex items-center bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-blue-500 transition-all shadow-lg hover:shadow-xl hover:-translate-y-1">
                Request Consultation
              </Link>
              <a href="#" className="inline-flex items-center bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 text-white px-8 py-4 rounded-lg font-semibold transition-all shadow-lg hover:-translate-y-1">
                Download Brochure
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content Area */}
      <section className="py-20">
        <div className="container mx-auto px-4 max-w-5xl">
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
            {/* Interactive Tabs Header */}
            <div className="flex flex-wrap border-b border-gray-100 bg-gray-50/50">
              {(['overview', 'features', 'benefits'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex-1 py-5 px-6 font-semibold text-sm sm:text-base transition-all duration-200 ${
                    activeTab === tab
                      ? 'bg-white text-blue-600 shadow-[inset_0_2px_0_#2563eb]'
                      : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'
                  }`}
                  aria-selected={activeTab === tab}
                  role="tab"
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {/* Tab Content Panel */}
            <div className="p-8 md:p-12 min-h-[400px]">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  transition={{ duration: 0.3, ease: "easeOut" }}
                  role="tabpanel"
                >
                  {tabContent[activeTab]}
                </motion.div>
              </AnimatePresence>
            </div>
          </div>

          {/* Bottom CTA */}
          <div className="mt-16 text-center">
            <p className="text-gray-600 mb-6">Ready to upgrade your infrastructure with our {solution.title} solution?</p>
            <Link to="/contact" className="inline-flex items-center text-blue-600 font-bold text-lg group">
              Speak with an expert today
              <span className="ml-2 bg-blue-100 text-blue-600 rounded-full p-1 group-hover:bg-blue-600 group-hover:text-white transition-all">
                <ArrowRight className="w-5 h-5" />
              </span>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default SolutionDetail;
