import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import MainLayout from './layouts/MainLayout';

// Lazy loading pages
const Home = React.lazy(() => import('./pages/Home'));
const About = React.lazy(() => import('./pages/About'));
const Solutions = React.lazy(() => import('./pages/Solutions'));
const SolutionDetail = React.lazy(() => import('./pages/SolutionDetail'));
const Industries = React.lazy(() => import('./pages/Industries'));
const Resources = React.lazy(() => import('./pages/Resources'));
const Contact = React.lazy(() => import('./pages/Contact'));

function App() {
  return (
    <HelmetProvider>
      <Router>
        <Suspense fallback={<div className="flex h-screen items-center justify-center">Loading...</div>}>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<Home />} />
              <Route path="about" element={<About />} />
              <Route path="solutions" element={<Solutions />} />
              <Route path="solutions/:id" element={<SolutionDetail />} />
              <Route path="industries" element={<Industries />} />
              <Route path="resources" element={<Resources />} />
              <Route path="contact" element={<Contact />} />
            </Route>
          </Routes>
        </Suspense>
      </Router>
    </HelmetProvider>
  );
}

export default App;
