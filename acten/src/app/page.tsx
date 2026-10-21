import Link from 'next/link';
import { prisma } from '@/lib/prisma';



export default async function Home() {
  const latestArticles = await prisma.article.findMany({
    where: { status: 'Published' },
    orderBy: { publishedAt: 'desc' },
    take: 3,
  });

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-acten-green text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-6xl font-bold font-serif text-acten-gold mb-6">
            Proclaiming Christ. Sharing the Gospel. Serving Communities.
          </h1>
          <p className="text-xl md:text-2xl mb-10 max-w-3xl mx-auto text-acten-ivory">
            Discover the evangelization activities, missions, formation programmes, and Gospel-centred initiatives of the Catholic Church across Nigeria.
          </p>
          <div className="flex justify-center space-x-4">
            <Link href="/events" className="bg-acten-gold text-acten-charcoal px-8 py-3 rounded-md font-bold hover:bg-white transition-colors">
              Explore Activities
            </Link>
            <Link href="/news" className="bg-transparent border-2 border-acten-gold text-acten-gold px-8 py-3 rounded-md font-bold hover:bg-acten-gold hover:text-acten-charcoal transition-colors">
              Latest News
            </Link>
          </div>
        </div>
      </section>

      {/* Featured News / Latest News */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-serif font-bold text-acten-burgundy mb-8 text-center">Latest from ACTEN</h2>
          {latestArticles.length === 0 ? (
            <p className="text-center text-gray-500">No news articles published yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {latestArticles.map((article) => (
                <div key={article.id} className="bg-acten-ivory rounded-lg overflow-hidden shadow-md">
                  <div className="h-48 bg-gray-300 flex items-center justify-center text-gray-500">Image Placeholder</div>
                  <div className="p-6">
                    <span className="text-sm text-acten-burgundy font-bold uppercase tracking-wider">News</span>
                    <h3 className="text-xl font-bold mt-2 mb-3">{article.title}</h3>
                    <p className="text-gray-600 mb-4 line-clamp-2">{article.summary || article.content}</p>
                    <Link href={`/news/${article.id}`} className="text-acten-green font-bold hover:underline">Read more &rarr;</Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Evangelization Activities */}
      <section className="py-16 bg-acten-ivory">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-serif font-bold text-acten-green mb-12">Our Mission in Action</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
            {['Parish Missions', 'Youth Evangelization', 'Digital Evangelization', 'Community Service'].map((activity, idx) => (
              <div key={idx} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                <h3 className="text-lg font-bold text-acten-charcoal mb-2">{activity}</h3>
                <p className="text-sm text-gray-600">Supporting and documenting the vibrant faith journey across Nigeria.</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter */}
      <section className="py-16 bg-acten-burgundy text-white">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-serif font-bold mb-4">Join Our Newsletter</h2>
          <p className="mb-8">Stay updated on the latest evangelization news and formation resources.</p>
          <form className="flex flex-col sm:flex-row justify-center max-w-lg mx-auto">
            <input type="email" placeholder="Email Address" className="px-4 py-3 rounded-l-md w-full text-black focus:outline-none" required />
            <button type="submit" className="bg-acten-gold text-acten-charcoal px-6 py-3 rounded-r-md font-bold hover:bg-white transition-colors mt-4 sm:mt-0">Subscribe</button>
          </form>
        </div>
      </section>
    </div>
  );
}
