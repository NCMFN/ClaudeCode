import Link from 'next/link';
import { Calendar, Tag, ArrowLeft, Share2 } from 'lucide-react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'News Article | ACTEN',
};

export default function ArticlePage() {
  // Demo content
  return (
    <div className="flex flex-col min-h-screen bg-brand-ivory">
      <article className="max-w-4xl mx-auto px-6 py-12 w-full">
        <Link href="/news" className="inline-flex items-center gap-2 text-brand-green font-medium mb-8 hover:text-brand-gold transition-colors text-sm">
          <ArrowLeft size={16} /> Back to News
        </Link>

        <header className="mb-10 text-center">
          <div className="flex items-center justify-center gap-4 text-xs font-semibold text-brand-burgundy uppercase tracking-wider mb-4">
            <span className="flex items-center gap-1"><Tag size={12}/> Parish Mission</span>
            <span>•</span>
            <span className="flex items-center gap-1"><Calendar size={12}/> March 15, 2026</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-serif text-brand-charcoal mb-6">
            Lenten Outreach Touches Hundreds in Rural Communities
          </h1>
          <p className="text-xl text-gray-600 italic">
            A united effort by trained evangelizers brings the sacraments and catechesis to remote villages.
          </p>
        </header>

        <div className="w-full bg-brand-light-grey aspect-video mb-10 flex items-center justify-center rounded-lg border border-gray-200">
           <span className="text-gray-400">Featured Image Placeholder</span>
        </div>

        <div className="prose prose-lg max-w-none text-gray-800 prose-headings:font-serif prose-headings:text-brand-green prose-a:text-brand-burgundy">
          <p>
            During this year&apos;s Lenten season, a team of trained evangelizers organized a comprehensive mission to remote villages, focusing on catechesis, prayer, and community service. The initiative brought the sacraments closer to those living far from the central parish.
          </p>
          <p>
            (This is a demonstration article. In the final version, this content will be loaded dynamically from the PostgreSQL database.)
          </p>
          <h3>A Call to Serve</h3>
          <p>
            The evangelization team spent three weeks preparing the curriculum and gathering resources for the outreach. The response from the local communities was overwhelming, with many families participating in the daily rosary and evening teachings.
          </p>
        </div>

        <footer className="mt-12 pt-8 border-t border-gray-200 flex justify-between items-center">
          <div className="text-sm text-gray-500">
            Report submitted by: <strong>St. Peter&apos;s Parish Team</strong>
          </div>
          <button className="flex items-center gap-2 text-brand-green hover:text-brand-gold transition-colors text-sm font-medium">
            <Share2 size={16} /> Share Article
          </button>
        </footer>
      </article>
    </div>
  );
}
