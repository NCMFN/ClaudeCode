import React, { useState, useEffect } from 'react';

interface Logo {
  name: string;
  type: string;
}

interface LogoCarouselProps {
  logos: Logo[];
}

const LogoCarousel: React.FC<LogoCarouselProps> = ({ logos }) => {
  const [position, setPosition] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPosition((prev) => (prev + 1) % logos.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [logos.length]);

  return (
    <div className="overflow-hidden relative w-full h-24 flex items-center justify-center">
      <div className="flex space-x-12 px-4 transition-transform duration-1000 ease-in-out" style={{ transform: `translateX(-${position * 10}%)` }}>
        {logos.concat(logos).map((logo, index) => (
          <div key={`${logo.name}-${index}`} className="flex items-center justify-center min-w-[150px]">
            <span className="text-2xl font-bold text-gray-400 grayscale opacity-70 hover:opacity-100 hover:grayscale-0 transition-all cursor-pointer">
              {logo.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LogoCarousel;
