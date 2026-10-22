import { Metadata } from 'next';
import Link from 'next/link';
import { prisma } from '@/lib/prisma';

export const metadata: Metadata = {
  title: 'Evangelization News | ACTEN',
  description: 'Latest news and updates on Catholic evangelization outreach across Nigeria.',
};



export default async function NewsPage() {
  const articles = await prisma.article.findMany({
    where: { status: 'Published' },
    orderBy: { publishedAt: 'desc' },
  });

  return (
    <div className="bg-acten-ivory min-h-screen pb-16">
      <div className="bg-acten-green py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-serif font-bold text-white mb-2">Evangelization News</h1>
          <p className="text-acten-gold">Reports from dioceses, parishes, and missions across Nigeria</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
        <div className="flex flex-col md:flex-row gap-8">
          {/* Sidebar / Filters */}
          <aside className="w-full md:w-1/4">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="font-bold text-lg mb-4 text-acten-charcoal border-b pb-2">Categories</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link href="#" className="hover:text-acten-green">Evangelization Outreach</Link></li>
                <li><Link href="#" className="hover:text-acten-green">Diocesan News</Link></li>
                <li><Link href="#" className="hover:text-acten-green">Parish Activities</Link></li>
                <li><Link href="#" className="hover:text-acten-green">Missionary Activities</Link></li>
                <li><Link href="#" className="hover:text-acten-green">Youth Evangelization</Link></li>
              </ul>
            </div>
          </aside>

          {/* Main Content */}
          <main className="w-full md:w-3/4">
            {articles.length === 0 ? (
              <div className="bg-white p-8 rounded-lg shadow-sm text-center">
                <p className="text-gray-500">No published articles available at the moment.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {articles.map((article) => (
                  <div key={article.id} className="bg-white rounded-lg overflow-hidden shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                    <div className="h-48 bg-gray-200 flex items-center justify-center">Image</div>
                    <div className="p-6">
                      <div className="flex justify-between items-center mb-3">
                        <span className="text-xs font-bold text-acten-burgundy uppercase">News</span>
                        <span className="text-xs text-gray-500">
                          {article.publishedAt ? new Date(article.publishedAt).toLocaleDateString() : ''}
                        </span>
                      </div>
                      <h3 className="text-xl font-bold mb-2 text-acten-charcoal">
                        <Link href={`/news/${article.id}`} className="hover:text-acten-green">
                          {article.title}
                        </Link>
                      </h3>
                      <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                        {article.summary || article.content.substring(0, 150) + '...'}
                      </p>
                      <Link href={`/news/${article.id}`} className="text-acten-green text-sm font-bold hover:underline">
                        Read full article &rarr;
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
