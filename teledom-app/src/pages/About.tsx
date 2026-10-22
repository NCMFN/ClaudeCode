import React from 'react';
import { Helmet } from 'react-helmet-async';
import { team, stats } from '../data';
import { motion } from 'framer-motion';

const About: React.FC = () => {
  const ceo = team[0];

  return (
    <div className="pt-20 bg-gray-50 min-h-screen">
      <Helmet>
        <title>Teledom International - About Us</title>
        <meta name="description" content="Learn more about Teledom International, our mission, and the leadership team driving IT and telecommunications innovation." />
      </Helmet>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 text-white py-24 relative overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img src="https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=1200" alt="Office building" className="w-full h-full object-cover opacity-30 mix-blend-overlay" />
          <div className="absolute inset-0 bg-gradient-to-t from-gray-900/80 to-transparent"></div>
        </div>
        <div className="container mx-auto px-4 text-center relative z-10">
          <h1 className="text-4xl md:text-6xl font-extrabold mb-6 drop-shadow-lg tracking-tight">About Teledom International</h1>
          <p className="text-xl max-w-3xl mx-auto text-blue-100 drop-shadow font-light leading-relaxed">
            A legacy of excellence in delivering cutting-edge IT and telecommunications solutions that empower enterprises worldwide.
          </p>
        </div>
      </section>

      {/* Mission & Vision */}
      <section id="identity" className="py-20 bg-white relative">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative rounded-2xl overflow-hidden shadow-2xl"
            >
              <div className="absolute inset-0 bg-gradient-to-tr from-blue-900/40 to-transparent z-10 mix-blend-multiply"></div>
              {/* Fallback image representing about.jpg */}
              <img src="https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&q=80&w=800" alt="About Teledom" className="w-full h-[500px] object-cover" />
              <div className="absolute bottom-4 left-4 z-20">
                 <span className="bg-black/50 backdrop-blur-md text-white text-xs px-2 py-1 rounded font-mono tracking-wider">[ PLACEHOLDER: about.jpg ]</span>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <div className="mb-12">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-1 bg-blue-600 rounded-full mr-4"></div>
                  <h2 className="text-3xl font-bold text-gray-900">Our Mission</h2>
                </div>
                <p className="text-gray-600 text-lg leading-relaxed">
                  To bridge the digital divide by providing robust, innovative, and scalable IT and telecommunications infrastructure that drives business success and technological advancement.
                </p>
              </div>

              <div>
                <div className="flex items-center mb-4">
                  <div className="w-10 h-1 bg-blue-600 rounded-full mr-4"></div>
                  <h2 className="text-3xl font-bold text-gray-900">Our Vision</h2>
                </div>
                <p className="text-gray-600 text-lg leading-relaxed">
                  To be the globally recognized leader in intelligent digital solutions, setting the standard for reliability, security, and enterprise connectivity.
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-gradient-to-b from-blue-50 to-white border-y border-gray-100">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                key={index}
                className="text-center p-8 bg-white rounded-2xl shadow-[0_4px_20px_rgb(0,0,0,0.04)] border border-gray-50 transform transition duration-300 hover:-translate-y-2 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)]"
              >
                <div className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 mb-3">{stat.value}</div>
                <div className="text-gray-500 font-bold uppercase tracking-widest text-sm">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Leadership Team - Meet the CEO */}
      <section id="team" className="py-24 bg-white">
        <div className="container mx-auto px-4 max-w-5xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-extrabold text-gray-900 tracking-tight">Meet the Leadership</h2>
          </div>

          <div className="bg-gray-50 rounded-3xl p-8 md:p-12 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100">
            <div className="flex flex-col md:flex-row items-center md:items-start gap-12">
              <div className="flex-shrink-0 relative group">
                 {/* Placeholder for Dr. Ekuwem's photo until asset is loaded */}
                 <div className="w-64 h-64 md:w-80 md:h-80 rounded-2xl shadow-xl overflow-hidden relative border-4 border-white">
                    <img src="https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&q=80&w=800" alt={ceo.name} className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
                    <div className="absolute inset-0 bg-gradient-to-t from-gray-900/60 to-transparent"></div>
                    <div className="absolute bottom-3 left-3">
                       <span className="bg-black/50 backdrop-blur-md text-white text-[10px] px-2 py-1 rounded font-mono tracking-widest">[ PLACEHOLDER: Dr Ekuwem-NKK5rSRO.jpg ]</span>
                    </div>
                 </div>
              </div>
              <div className="text-center md:text-left flex-1">
                <h3 className="text-4xl font-bold text-gray-900 mb-2">{ceo.name}</h3>
                <p className="text-blue-600 font-bold text-xl uppercase tracking-wide mb-6">{ceo.role}</p>
                <div className="prose prose-lg text-gray-600 leading-relaxed max-w-none">
                  <p>{ceo.bio}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Our Work / Gallery Section */}
      <section id="work" className="py-24 bg-gray-900 text-white">
        <div className="container mx-auto px-4 max-w-6xl">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-extrabold tracking-tight mb-4 text-white">Our Work in Action</h2>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto font-light">Glimpses of our major infrastructure and enterprise deployments across Nigeria.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[
                  { title: "Telecom Tower Setup", img: "https://images.unsplash.com/photo-1544377193-33dcf4d68fb5?auto=format&fit=crop&q=80&w=800" },
                  { title: "Enterprise Data Center", img: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&q=80&w=800" },
                  { title: "Fiber Optic Cabling", img: "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&q=80&w=800" },
                  { title: "Smart Classroom Deploy", img: "https://images.unsplash.com/photo-1588702547923-7093a6c3ba33?auto=format&fit=crop&q=80&w=800" },
                  { title: "Security Command Center", img: "https://images.unsplash.com/photo-1557597774-9d273605dfa9?auto=format&fit=crop&q=80&w=800" },
                  { title: "Identity Capture Station", img: "https://images.unsplash.com/photo-1581092334651-ddf26d9a09d0?auto=format&fit=crop&q=80&w=800" },
                ].map((item, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, scale: 0.95 }}
                      whileInView={{ opacity: 1, scale: 1 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.1 }}
                      className="group relative aspect-[4/3] rounded-xl overflow-hidden bg-gray-800"
                    >
                        <img src={item.img} alt={item.title} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110 opacity-80 group-hover:opacity-100" />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div className="absolute bottom-0 left-0 p-6 translate-y-4 group-hover:translate-y-0 opacity-0 group-hover:opacity-100 transition-all duration-300">
                          <h4 className="text-lg font-bold text-white">{item.title}</h4>
                          <p className="text-sm text-blue-300 font-medium tracking-wide">[ Gallery Image {i+1} ]</p>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
      </section>

    </div>
  );
};

export default About;
