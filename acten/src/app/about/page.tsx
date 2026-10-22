import { BookOpen, Target, Heart } from 'lucide-react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About ACTEN | Association of Catholic Trained Evangelizers',
  description: 'Learn about the mission, vision, and history of ACTEN in Nigeria.',
};

export default function AboutPage() {
  return (
    <div className="flex flex-col min-h-screen bg-brand-ivory">
      {/* Page Header */}
      <div className="bg-brand-green py-16 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-serif text-white mb-4">About ACTEN</h1>
          <p className="text-brand-gold text-lg">Association of Catholic Trained Evangelizers in Nigeria</p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Intro */}
        <section className="mb-16 prose prose-lg max-w-none text-brand-charcoal">
          <p className="text-xl leading-relaxed text-gray-700">
            ACTEN is a national body focused on the evangelization mission of the Catholic Church in Nigeria.
            We serve as a central platform for documenting, coordinating, and promoting activities that proclaim Jesus Christ
            and bring the Gospel to individuals, families, and communities across the nation.
          </p>
        </section>

        {/* Mission & Vision */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          <div className="bg-white p-8 rounded-lg shadow-sm border border-brand-light-grey">
            <div className="flex items-center gap-3 mb-4 text-brand-green">
              <Target size={28} />
              <h2 className="text-2xl font-serif">Our Mission</h2>
            </div>
            <p className="text-gray-600 leading-relaxed italic border-l-4 border-brand-gold pl-4">
              &quot;To promote the evangelization mission of the Catholic Church in Nigeria by documenting,
              communicating, and supporting activities that proclaim Jesus Christ, strengthen Christian faith,
              encourage discipleship, and bring the Gospel to individuals, families, and communities.&quot;
            </p>
          </div>

          <div className="bg-white p-8 rounded-lg shadow-sm border border-brand-light-grey">
            <div className="flex items-center gap-3 mb-4 text-brand-green">
              <Heart size={28} />
              <h2 className="text-2xl font-serif">Our Vision</h2>
            </div>
            <p className="text-gray-600 leading-relaxed italic border-l-4 border-brand-gold pl-4">
              &quot;A vibrant community of trained Catholic evangelizers in Nigeria, committed to proclaiming
              the Gospel, nurturing Christian faith, and witnessing to Christ in every part of society.&quot;
            </p>
          </div>
        </div>

        {/* Objectives */}
        <section className="mb-16">
          <h2 className="text-3xl font-serif text-brand-green mb-8 border-b pb-2">Core Objectives</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              "Promote Catholic evangelization activities.",
              "Document missions and outreach programmes.",
              "Support evangelizer formation and development.",
              "Share approved Catholic teaching and faith resources.",
              "Encourage participation in evangelization initiatives.",
              "Preserve a reliable record of ACTEN activities.",
              "Promote Christian witness through service and community engagement."
            ].map((objective, idx) => (
              <div key={idx} className="flex items-start gap-3 bg-white p-4 rounded border border-brand-light-grey">
                <BookOpen className="text-brand-gold shrink-0 mt-1" size={20} />
                <span className="text-gray-700">{objective}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Leadership Placeholder */}
        <section className="bg-white p-8 rounded-lg shadow-sm border border-brand-light-grey text-center">
          <h2 className="text-2xl font-serif text-brand-green mb-4">Leadership & Structure</h2>
          <p className="text-gray-600 mb-6">
            Detailed information regarding our national leadership, diocesan structure, and organizational history is currently being updated and verified.
          </p>
          <div className="inline-block px-4 py-2 bg-brand-light-grey text-gray-500 text-sm rounded border border-gray-300">
            Verified institutional details pending publication.
          </div>
        </section>
      </div>
    </div>
  );
}
