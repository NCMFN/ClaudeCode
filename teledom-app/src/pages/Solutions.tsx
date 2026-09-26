import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import { solutions } from '../data';

const Solutions: React.FC = () => {
  return (
    <div className="pt-20">
      <Helmet>
        <title>Teledom - Solutions</title>
        <meta name="description" content="Explore Teledom's IT and telecommunication solutions." />
      </Helmet>
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold mb-12">Our Solutions</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {solutions.map((solution) => (
            <Link
              key={solution.id}
              to={`/solutions/${solution.id}`}
              className="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border border-gray-100"
            >
              <h2 className="text-2xl font-semibold mb-3 text-blue-900">{solution.title}</h2>
              <p className="text-gray-600">{solution.description}</p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Solutions;
