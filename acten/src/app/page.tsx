import Link from "next/link";
import { ArrowRight, Calendar, BookOpen, Users, MapPin } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-brand-green text-white py-24 px-6 overflow-hidden">
        {/* Abstract background elements mimicking stained glass or light */}
        <div className="absolute top-0 right-0 opacity-10 transform translate-x-1/4 -translate-y-1/4">
          <svg width="600" height="600" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="50" fill="#C8A45D" />
          </svg>
        </div>

        <div className="max-w-7xl mx-auto relative z-10 flex flex-col items-center text-center">
          <div className="mb-6 inline-block bg-brand-gold bg-opacity-20 text-brand-gold px-4 py-1 rounded-full text-sm font-semibold tracking-wider uppercase border border-brand-gold/30">
            Welcome to ACTEN
          </div>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-serif font-bold leading-tight mb-6 max-w-4xl">
            Proclaiming Christ. <span className="text-brand-gold">Sharing the Gospel.</span> Serving Communities.
          </h1>
          <p className="text-lg md:text-xl text-gray-200 mb-10 max-w-2xl leading-relaxed">
            Discover the evangelization activities, missions, formation programmes, and Gospel-centred initiatives of the Catholic Church across Nigeria.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
            <Link
              href="/events"
              className="bg-brand-gold text-brand-green px-8 py-3 rounded font-bold hover:bg-white transition-colors flex items-center justify-center gap-2 shadow-lg"
            >
              Explore Activities
              <ArrowRight size={18} />
            </Link>
            <Link
              href="/news"
              className="bg-transparent border border-white text-white px-8 py-3 rounded font-bold hover:bg-white/10 transition-colors flex items-center justify-center"
            >
              Read Latest News
            </Link>
          </div>
        </div>
      </section>

      {/* Featured Evangelization Story */}
      <section className="py-16 px-6 bg-brand-ivory">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-end mb-8 border-b border-brand-light-grey pb-4">
            <h2 className="text-3xl font-serif text-brand-green">Featured Report</h2>
            <Link href="/reports" className="text-brand-burgundy font-medium hover:underline flex items-center gap-1 text-sm">
              View all reports <ArrowRight size={14} />
            </Link>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-brand-light-grey overflow-hidden flex flex-col md:flex-row">
            <div className="md:w-1/2 bg-brand-light-grey min-h-[300px] flex items-center justify-center relative">
              <span className="text-gray-400">Image Placeholder</span>
            </div>
            <div className="p-8 md:w-1/2 flex flex-col justify-center">
              <span className="text-xs font-bold text-brand-burgundy uppercase tracking-wider mb-2">Parish Mission</span>
              <h3 className="text-2xl font-serif text-brand-charcoal mb-4">
                Lenten Outreach Touches Hundreds in Rural Communities
              </h3>
              <p className="text-gray-600 mb-6 line-clamp-3">
                During this year&apos;s Lenten season, a team of trained evangelizers organized a comprehensive mission to remote villages, focusing on catechesis, prayer, and community service. The initiative brought the sacraments closer to those living far from the central parish.
              </p>
              <div className="flex items-center justify-between text-sm text-gray-500 mt-auto">
                <span className="flex items-center gap-1"><MapPin size={14}/> Abuja Archdiocese</span>
                <span>March 15, 2026</span>
              </div>
              <Link href="/news/sample" className="inline-block mt-6 text-brand-green font-semibold hover:text-brand-gold transition-colors">
                Read Full Story →
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Navigation Cards */}
      <section className="py-12 px-6 bg-white">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-brand-ivory p-8 rounded-lg border border-brand-light-grey hover:shadow-md transition-shadow group">
            <div className="bg-brand-green text-brand-gold w-12 h-12 rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <BookOpen size={24} />
            </div>
            <h3 className="text-xl font-serif text-brand-green mb-3">Formation Resources</h3>
            <p className="text-gray-600 mb-6 text-sm">Access approved Catholic teaching materials, scripture reflections, and guides for effective evangelization.</p>
            <Link href="/resources" className="text-brand-burgundy font-medium text-sm hover:underline">Browse Library</Link>
          </div>

          <div className="bg-brand-ivory p-8 rounded-lg border border-brand-light-grey hover:shadow-md transition-shadow group">
            <div className="bg-brand-green text-brand-gold w-12 h-12 rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Calendar size={24} />
            </div>
            <h3 className="text-xl font-serif text-brand-green mb-3">Upcoming Events</h3>
            <p className="text-gray-600 mb-6 text-sm">Find conventions, training seminars, and diocesan mission activities happening near you.</p>
            <Link href="/events" className="text-brand-burgundy font-medium text-sm hover:underline">View Calendar</Link>
          </div>

          <div className="bg-brand-ivory p-8 rounded-lg border border-brand-light-grey hover:shadow-md transition-shadow group">
            <div className="bg-brand-green text-brand-gold w-12 h-12 rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Users size={24} />
            </div>
            <h3 className="text-xl font-serif text-brand-green mb-3">Submit a Report</h3>
            <p className="text-gray-600 mb-6 text-sm">Are you an authorized representative? Share news of your local Catholic evangelization efforts with the national community.</p>
            <Link href="/submit" className="text-brand-burgundy font-medium text-sm hover:underline">Submit Now</Link>
          </div>
        </div>
      </section>

      {/* About Preview */}
      <section className="py-16 px-6 bg-brand-green text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-serif text-brand-gold mb-6">About ACTEN</h2>
          <p className="text-lg mb-8 leading-relaxed text-gray-200">
            The Association of Catholic Trained Evangelizers in Nigeria is committed to proclaiming the Gospel, nurturing Christian faith, and witnessing to Christ in every part of society.
          </p>
          <Link href="/about" className="inline-block border-2 border-brand-gold text-brand-gold px-6 py-2 rounded font-medium hover:bg-brand-gold hover:text-brand-green transition-colors">
            Learn More About Our Mission
          </Link>
        </div>
      </section>
    </div>
  );
}
