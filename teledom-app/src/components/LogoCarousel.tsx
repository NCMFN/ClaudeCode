import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface Logo {
  name: string;
  type: string;
}

interface LogoCarouselProps {
  logos: Logo[];
}

const LogoCarousel: React.FC<LogoCarouselProps> = ({ logos }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  const [visibleItems, setVisibleItems] = useState(5);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 640) setVisibleItems(2);
      else if (window.innerWidth < 1024) setVisibleItems(3);
      else setVisibleItems(5);
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const totalPages = Math.ceil(logos.length / visibleItems);

  useEffect(() => {
    if (isHovered) return;

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % totalPages);
    }, 4000);
    return () => clearInterval(interval);
  }, [totalPages, isHovered]);

  const nextSlide = () => setCurrentIndex((prev) => (prev + 1) % totalPages);
  const prevSlide = () => setCurrentIndex((prev) => (prev - 1 + totalPages) % totalPages);

  const currentLogos = logos.slice(currentIndex * visibleItems, (currentIndex + 1) * visibleItems);

  return (
    <div
      className="relative w-full py-8"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-center justify-between">
        <button
          onClick={prevSlide}
          className="p-2 rounded-full bg-gray-50 text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors shadow-sm z-10"
          aria-label="Previous logos"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>

        <div className="flex-1 overflow-hidden px-4">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentIndex}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="flex items-center justify-around space-x-8"
            >
              {currentLogos.map((logo, index) => (
                <div key={`${logo.name}-${index}`} className="flex flex-col items-center justify-center space-y-2">
                  <div className="h-16 w-32 bg-gray-50 rounded-lg flex items-center justify-center border border-gray-100 shadow-sm group hover:border-blue-200 hover:shadow-md transition-all">
                    {/* Simulated Logo based on prompt rules: clean text-based wordmark placeholder */}
                    <span className="text-xl font-black tracking-tight text-gray-500 group-hover:text-blue-600 transition-colors text-center px-2 leading-tight">
                      {logo.name}
                    </span>
                  </div>
                  <span className="text-[10px] uppercase font-semibold text-gray-400 tracking-wider">
                    {logo.type}
                  </span>
                </div>
              ))}
            </motion.div>
          </AnimatePresence>
        </div>

        <button
          onClick={nextSlide}
          className="p-2 rounded-full bg-gray-50 text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors shadow-sm z-10"
          aria-label="Next logos"
        >
          <ChevronRight className="w-6 h-6" />
        </button>
      </div>

      {/* Dots Indicator */}
      <div className="flex justify-center mt-8 space-x-2">
        {Array.from({ length: totalPages }).map((_, i) => (
          <button
            key={i}
            onClick={() => setCurrentIndex(i)}
            className={`w-2.5 h-2.5 rounded-full transition-all ${
              i === currentIndex ? 'bg-blue-600 w-6' : 'bg-gray-300 hover:bg-gray-400'
            }`}
            aria-label={`Go to slide ${i + 1}`}
          />
        ))}
      </div>
    </div>
  );
};

export default LogoCarousel;
