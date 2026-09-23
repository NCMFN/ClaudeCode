import React from 'react';
import { Helmet } from 'react-helmet-async';
import { team, stats } from '../data';

const About: React.FC = () => {
  return (
    <div className="pt-20">
      <Helmet>
        <title>Teledom - About Us</title>
        <meta name="description" content="Learn more about Teledom, our mission, and the leadership team driving IT and telecommunications innovation." />
      </Helmet>

      {/* Hero Section */}
      <section className="bg-blue-900 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">About Teledom</h1>
          <p className="text-xl max-w-3xl mx-auto text-blue-100">
            A legacy of excellence in delivering cutting-edge IT and telecommunications solutions that empower enterprises worldwide.
          </p>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <img
                src="https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=1200"
                alt="Corporate office building exterior"
                className="rounded-lg shadow-xl"
              />
            </div>
            <div>
              <h2 className="text-3xl font-bold mb-6 text-gray-900">Our Mission</h2>
              <p className="text-gray-600 mb-8 text-lg">
                To bridge the digital divide by providing robust, innovative, and scalable IT and telecommunications infrastructure that drives business success and technological advancement.
              </p>

              <h2 className="text-3xl font-bold mb-6 text-gray-900">Our Vision</h2>
              <p className="text-gray-600 text-lg">
                To be the globally recognized leader in intelligent digital solutions, setting the standard for reliability, security, and enterprise connectivity.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-blue-50">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-blue-600 mb-2">{stat.value}</div>
                <div className="text-gray-600 font-medium uppercase tracking-wide text-sm">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Leadership Team */}
      <section id="team" className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">Our Leadership Team</h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {team.map((member, index) => (
              <div key={index} className="text-center group">
                <div className="relative w-48 h-48 mx-auto mb-6 rounded-full overflow-hidden">
                  <img
                    src={member.image}
                    alt={`${member.name} - ${member.role}`}
                    className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-300"
                  />
                </div>
                <h3 className="text-xl font-bold text-gray-900">{member.name}</h3>
                <p className="text-blue-600 font-medium mt-1">{member.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;
