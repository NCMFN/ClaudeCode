import React from 'react';
import { Helmet } from 'react-helmet-async';
import { industries } from '../data';
import { Link } from 'react-router-dom';

const Industries: React.FC = () => {
  return (
    <div className="pt-20">
      <Helmet>
        <title>Teledom - Industries We Serve</title>
        <meta name="description" content="Discover the various industries Teledom empowers through advanced IT and telecommunication solutions." />
      </Helmet>

      <section className="bg-blue-900 text-white py-20 text-center">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">Industries We Serve</h1>
          <p className="text-xl text-blue-100 max-w-2xl mx-auto">
            Tailored digital infrastructure solutions designed for the unique challenges of diverse sectors.
          </p>
        </div>
      </section>

      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {industries.map((industry) => (
              <div key={industry.id} id={industry.id} className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                <h2 className="text-2xl font-bold text-blue-900 mb-4">{industry.title}</h2>
                <p className="text-gray-600 mb-6">{industry.description}</p>
                <Link to="/contact" className="text-blue-600 font-medium hover:text-blue-800 flex items-center">
                  Discuss solutions for your industry
                  <span className="ml-2">→</span>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Industries;
