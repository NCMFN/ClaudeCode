import React from 'react';
import { Helmet } from 'react-helmet-async';

const Resources: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Resources - Teledom International</title>
        <meta name="description" content="Download company profiles, solution brochures, and other resources." />
      </Helmet>

      <div className="bg-gray-50 py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl mb-4">
              Resources & Downloads
            </h1>
            <p className="text-xl text-gray-500">
              Access our company profile and solution brochures.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
               <h3 className="text-2xl font-bold text-gray-900 mb-4">Teledom International Company Profile</h3>
               <p className="text-gray-600 mb-6">Learn more about our comprehensive IT, telecommunication, and security solutions.</p>
               <a href="#" className="inline-flex items-center bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 transition-colors shadow">
                 <span className="mr-2">[PDF]</span> Download Company Profile
               </a>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Resources;
