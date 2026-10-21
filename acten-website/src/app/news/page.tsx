import Link from "next/link";
import prisma from "@/lib/prisma";

export default async function NewsPage() {
  const articles = await prisma.article.findMany({
    where: { published: true },
    orderBy: { createdAt: 'desc' },
    include: { category: true, author: true }
  });

  return (
    <div className="flex flex-col min-h-screen bg-white">
      <div className="bg-acten-green text-acten-ivory py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="font-serif text-4xl md:text-5xl font-bold mb-4 text-acten-gold">Evangelization News</h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto">
            Latest updates, activities, and missions across the Catholic Church in Nigeria.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {articles.length === 0 ? (
          <div className="text-center py-20 bg-gray-50 rounded-lg">
            <h2 className="text-2xl font-serif text-acten-green mb-2">No Articles Found</h2>
            <p className="text-gray-600">Check back later for the latest evangelization news.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {articles.map((article) => (
              <div key={article.id} className="bg-white rounded-lg overflow-hidden shadow-sm border border-gray-100 hover:shadow-md transition-shadow flex flex-col">
                <div className="relative h-48 bg-gray-200">
                  {article.imageUrl ? (
                    <img src={article.imageUrl} alt={article.title} className="w-full h-full object-cover" />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center text-gray-400">Image Placeholder</div>
                  )}
                </div>
                <div className="p-6 flex-grow flex flex-col">
                  <div className="flex items-center gap-2 mb-3">
                    {article.category && (
                      <span className="text-xs font-bold uppercase tracking-wider text-acten-burgundy">{article.category.name}</span>
                    )}
                    <span className="text-xs text-gray-500">{new Date(article.createdAt).toLocaleDateString()}</span>
                  </div>
                  <h3 className="font-serif text-xl font-bold mb-3 hover:text-acten-burgundy transition-colors">
                    <Link href={`/news/${article.slug}`}>{article.title}</Link>
                  </h3>
                  <p className="text-gray-600 mb-4 line-clamp-3 text-sm">{article.summary}</p>
                  <div className="mt-auto pt-4 border-t border-gray-100 flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900">{article.author?.name || 'ACTEN'}</span>
                    <Link href={`/news/${article.slug}`} className="text-sm font-bold text-acten-green hover:text-acten-burgundy">
                      Read more &rarr;
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
