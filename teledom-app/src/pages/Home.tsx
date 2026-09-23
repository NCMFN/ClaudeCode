import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import TestimonialCarousel from '../components/TestimonialCarousel';
import LogoCarousel from '../components/LogoCarousel';
import { testimonials, partners } from '../data';

const Home: React.FC = () => {
  return (
    <div className="pt-20">
      <Helmet>
        <title>Teledom - Home</title>
        <meta name="description" content="Welcome to Teledom, providing top IT and telecommunication solutions." />
      </Helmet>

      {/* Hero Section */}
      <section className="relative bg-blue-900 text-white py-32 overflow-hidden">
        <img
          src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=1920"
          alt="Telecom tower skyline"
          className="absolute inset-0 w-full h-full object-cover opacity-20"
        />
        <div className="container mx-auto px-4 relative z-10 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">Empowering Your Digital Future</h1>
          <p className="text-xl md:text-2xl mb-10 max-w-3xl mx-auto text-blue-100">
            Innovative IT and Telecommunication solutions for enterprises that demand excellence.
          </p>
          <div className="space-x-4">
            <Link to="/contact" className="bg-blue-500 hover:bg-blue-400 text-white px-8 py-3 rounded-md font-semibold text-lg transition-colors">
              Get Started
            </Link>
          </div>
        </div>
      </section>

      {/* Partners Logo Carousel */}
      <section className="py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <p className="text-center text-sm font-semibold text-gray-500 uppercase tracking-wide mb-8">Trusted by Industry Leaders</p>
          <LogoCarousel logos={partners} />
        </div>
      </section>

      {/* Testimonials Carousel */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">What Our Clients Say</h2>
          <TestimonialCarousel testimonials={testimonials} />
        </div>
      </section>
    </div>
  );
};

export default Home;
