import React from 'react';
import { Helmet } from 'react-helmet-async';
import { resources } from '../data';

const Resources: React.FC = () => {
  return (
    <div className="pt-20">
      <Helmet>
        <title>Teledom - Resources & Insights</title>
        <meta name="description" content="Stay updated with the latest insights, whitepapers, and case studies from Teledom." />
      </Helmet>

      <section className="bg-blue-900 text-white py-20 text-center">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">Resources & Insights</h1>
          <p className="text-xl text-blue-100 max-w-2xl mx-auto">
            Industry knowledge, technical guides, and company news to help you stay ahead.
          </p>
        </div>
      </section>

      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="space-y-6">
            {resources.map((resource, index) => (
              <div key={index} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex flex-col sm:flex-row justify-between items-start sm:items-center">
                <div>
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-1 rounded">
                      {resource.type}
                    </span>
                    <span className="text-sm text-gray-500">{resource.date}</span>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mt-1">{resource.title}</h3>
                </div>
                <a href={resource.link} className="mt-4 sm:mt-0 inline-flex items-center text-blue-600 hover:text-blue-800 font-medium">
                  Read More <span className="ml-1">→</span>
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Resources;
