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
    return <div className="pt-32 text-center text-2xl">Solution not found</div>;
  }

  const tabContent = {
    overview: (
      <div className="space-y-4">
        <h3 className="text-2xl font-semibold">Overview</h3>
        <p className="text-gray-700 leading-relaxed">
          {solution.description} Discover how our specialized {solution.title.toLowerCase()} solution can streamline your operations and drive growth.
        </p>
      </div>
    ),
    features: (
      <div className="space-y-4">
        <h3 className="text-2xl font-semibold">Key Features</h3>
        <ul className="list-disc pl-5 space-y-2 text-gray-700">
          <li>Scalable architecture tailored to your needs.</li>
          <li>24/7 monitoring and support.</li>
          <li>Seamless integration with existing systems.</li>
        </ul>
      </div>
    ),
    benefits: (
      <div className="space-y-4">
        <h3 className="text-2xl font-semibold">Business Benefits</h3>
        <ul className="list-disc pl-5 space-y-2 text-gray-700">
          <li>Reduced operational costs.</li>
          <li>Enhanced security and compliance.</li>
          <li>Improved overall performance and reliability.</li>
        </ul>
      </div>
    )
  };

  return (
    <div className="pt-20">
      <Helmet>
        <title>{`Teledom - ${solution.title}`}</title>
        <meta name="description" content={solution.description} />
      </Helmet>

      {/* Hero */}
      <section className="bg-blue-50 py-20 border-b border-gray-200">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-blue-900 mb-4">{solution.title}</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">{solution.description}</p>
          <div className="mt-8 space-x-4">
            <Link to="/contact" className="inline-block bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 transition-colors">
              Request a Consultation
            </Link>
            <a href="#pdf" className="inline-block bg-white text-blue-600 border border-blue-600 px-6 py-3 rounded-md font-medium hover:bg-blue-50 transition-colors">
              Download Solution Brochure
            </a>
          </div>
        </div>
      </section>

      {/* Interactive Tabs */}
      <section className="py-16">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="flex border-b border-gray-200 mb-8 overflow-x-auto">
            {(['overview', 'features', 'benefits'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-6 font-medium text-sm sm:text-base whitespace-nowrap transition-colors ${
                  activeTab === tab
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                aria-selected={activeTab === tab}
                role="tab"
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          <div className="min-h-[200px]">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
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
