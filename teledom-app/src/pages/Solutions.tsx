import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import { solutions } from '../data';
import { motion } from 'framer-motion';

const Solutions: React.FC = () => {
  return (
    <div className="pt-20">
      <Helmet>
        <title>Teledom Group - Our Solutions</title>
        <meta name="description" content="Explore Teledom's comprehensive IT, networking, security, and telecommunication solutions." />
      </Helmet>

      {/* Page Header */}
      <section className="bg-gray-900 py-20 text-white border-b-4 border-blue-600 relative overflow-hidden">
        <div className="absolute inset-0 z-0 opacity-20">
          <img src="/assets/software.jpg" alt="Solutions Background" className="w-full h-full object-cover grayscale" />
        </div>
        <div className="container mx-auto px-4 relative z-10">
          <motion.h1
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-5xl font-bold mb-4"
          >
            Our Core Solutions
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xl text-gray-300 max-w-2xl"
          >
            Delivering robust, innovative, and scalable IT and telecommunications infrastructure.
          </motion.p>
        </div>
      </section>

      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {solutions.map((solution, index) => (
              <motion.div
                key={solution.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
              >
                <Link
                  to={`/solutions/${solution.id}`}
                  className="flex flex-col h-full bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 group overflow-hidden"
                >
                  <div className="h-48 overflow-hidden relative">
                    <img
                      src={solution.image}
                      alt={solution.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-blue-900/10 group-hover:bg-transparent transition-colors"></div>
                  </div>
                  <div className="p-6 flex-grow flex flex-col">
                    <h2 className="text-xl font-bold mb-3 text-gray-900 group-hover:text-blue-600 transition-colors">{solution.title}</h2>
                    <p className="text-gray-600 mb-4 flex-grow">{solution.description}</p>
                    <span className="text-blue-600 font-semibold flex items-center">
                      Learn more <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
                    </span>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Solutions;
