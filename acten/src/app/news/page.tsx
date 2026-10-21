import Link from 'next/link';
import { Calendar, Tag } from 'lucide-react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Evangelization News | ACTEN',
  description: 'Latest news and reports on Catholic evangelization activities across Nigeria.',
};

export default function NewsPage() {
  // Placeholder data for demonstration
  const news = [
    {
      id: "1",
      title: "Lenten Outreach Touches Hundreds in Rural Communities",
      category: "Parish Mission",
      date: "March 15, 2026",
      summary: "During this year's Lenten season, a team of trained evangelizers organized a comprehensive mission to remote villages, focusing on catechesis, prayer, and community service.",
    },
    {
      id: "2",
      title: "National Evangelizers Conference Announced for Abuja",
      category: "ACTEN Announcements",
      date: "February 28, 2026",
      summary: "The annual gathering of Catholic evangelizers will take place at the Catholic Secretariat of Nigeria this October, focusing on digital discipleship.",
    },
    {
      id: "3",
      title: "Youth Ministry Launches 'Street Disciples' Initiative",
      category: "Youth Evangelization",
      date: "February 10, 2026",
      summary: "Young Catholics in Lagos have begun a new peer-to-peer evangelization programme aimed at university students and young professionals.",
    }
  ];

  return (
    <div className="flex flex-col min-h-screen bg-brand-ivory">
      <div className="bg-brand-green py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-serif text-white mb-2">Evangelization News</h1>
          <p className="text-brand-gold text-lg">Reports from the mission field across Nigeria</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12 w-full flex flex-col md:flex-row gap-8">
        {/* Sidebar Filters */}
        <aside className="w-full md:w-1/4">
          <div className="bg-white p-6 rounded-lg border border-brand-light-grey sticky top-24">
            <h3 className="font-serif text-xl text-brand-green mb-4 border-b pb-2">Categories</h3>
            <ul className="space-y-3 text-sm text-gray-600">
              <li><Link href="#" className="hover:text-brand-burgundy font-medium">All News</Link></li>
              <li><Link href="#" className="hover:text-brand-burgundy">Diocesan News</Link></li>
              <li><Link href="#" className="hover:text-brand-burgundy">Parish Activities</Link></li>
              <li><Link href="#" className="hover:text-brand-burgundy">Youth Evangelization</Link></li>
              <li><Link href="#" className="hover:text-brand-burgundy">Evangelizer Formation</Link></li>
              <li><Link href="#" className="hover:text-brand-burgundy">ACTEN Announcements</Link></li>
            </ul>
          </div>
        </aside>

        {/* Main Content */}
        <main className="w-full md:w-3/4">
          <div className="grid gap-6">
            {news.map((item) => (
              <article key={item.id} className="bg-white p-6 rounded-lg border border-brand-light-grey flex flex-col md:flex-row gap-6 hover:shadow-md transition-shadow">
                <div className="md:w-1/3 bg-brand-light-grey rounded min-h-[160px] flex items-center justify-center">
                  <span className="text-gray-400 text-sm">Image</span>
                </div>
                <div className="md:w-2/3 flex flex-col">
                  <div className="flex items-center gap-4 text-xs font-semibold text-brand-burgundy uppercase tracking-wider mb-2">
                    <span className="flex items-center gap-1"><Tag size={12}/> {item.category}</span>
                  </div>
                  <Link href={`/news/${item.id}`}>
                    <h2 className="text-2xl font-serif text-brand-charcoal mb-3 hover:text-brand-green transition-colors">{item.title}</h2>
                  </Link>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">{item.summary}</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500 mt-auto pt-4 border-t border-gray-100">
                    <span className="flex items-center gap-1"><Calendar size={12}/> {item.date}</span>
                    <Link href={`/news/${item.id}`} className="ml-auto font-medium text-brand-green hover:text-brand-gold transition-colors">
                      Read Article →
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}
