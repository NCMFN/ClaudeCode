import React from 'react';
import { motion } from 'framer-motion';

interface LogoCarouselProps {
  logos: { name: string; type?: string; image?: string }[];
}

const LogoCarousel: React.FC<LogoCarouselProps> = ({ logos }) => {
  // We duplicate the logos array to create a seamless infinite scroll effect
  const duplicatedLogos = [...logos, ...logos];

  return (
    <div className="w-full overflow-hidden bg-white py-8 relative">
      {/* Gradient masks for smooth fading edges */}
      <div className="absolute left-0 top-0 bottom-0 w-16 md:w-32 z-10 bg-gradient-to-r from-white to-transparent pointer-events-none"></div>
      <div className="absolute right-0 top-0 bottom-0 w-16 md:w-32 z-10 bg-gradient-to-l from-white to-transparent pointer-events-none"></div>

      <motion.div
        className="flex items-center space-x-12 md:space-x-24 w-max"
        animate={{
          x: ['0%', '-50%'],
        }}
        transition={{
          x: {
            repeat: Infinity,
            repeatType: 'loop',
            duration: 35, // Slower, smoother scroll
            ease: 'linear',
          },
        }}
      >
        {duplicatedLogos.map((logo, index) => (
          <div
            key={index}
            className="flex flex-col items-center justify-center min-w-[150px] md:min-w-[200px]"
          >
            {logo.image ? (
              <img
                src={logo.image}
                alt={`${logo.name} logo`}
                className="h-16 md:h-20 object-contain grayscale hover:grayscale-0 transition-all duration-300"
              />
            ) : (
              // Fallback for missing logo assets - flagged for client
              <div className="px-4 py-3 bg-gray-50 border border-gray-100 rounded text-center grayscale hover:grayscale-0 transition-all duration-300 shadow-sm">
                <span className="text-gray-800 font-bold text-sm md:text-base leading-tight">
                  {logo.name}
                </span>
                {/* Note: Real logo image required */}
              </div>
            )}
          </div>
        ))}
      </motion.div>
    </div>
  );
};

export default LogoCarousel;
