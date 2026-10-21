import Link from "next/link";
import prisma from "@/lib/prisma";
import { notFound } from "next/navigation";

export default async function ArticlePage({ params }: { params: { slug: string } }) {
  const article = await prisma.article.findUnique({
    where: { slug: params.slug },
    include: { category: true, author: true }
  });

  if (!article) {
    notFound();
  }

  return (
    <div className="flex flex-col min-h-screen bg-white">
      <div className="bg-acten-green text-acten-ivory py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
           <div className="flex justify-center items-center gap-4 mb-6">
            {article.category && (
              <span className="bg-acten-gold text-acten-green px-3 py-1 text-xs font-bold uppercase tracking-wider rounded-full">
                {article.category.name}
              </span>
            )}
            <span className="text-acten-ivory/80 text-sm">
              {new Date(article.createdAt).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
            </span>
          </div>
          <h1 className="font-serif text-3xl md:text-5xl font-bold mb-6 text-white leading-tight">
            {article.title}
          </h1>
          <p className="text-lg text-acten-ivory/90">
            By {article.author?.name || 'ACTEN Contributor'}
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {article.imageUrl && (
          <div className="mb-12 rounded-xl overflow-hidden shadow-lg">
            <img src={article.imageUrl} alt={article.title} className="w-full h-auto object-cover max-h-[500px]" />
          </div>
        )}

        {article.summary && (
          <div className="mb-10 text-xl text-gray-600 font-serif italic border-l-4 border-acten-gold pl-6 py-2">
            {article.summary}
          </div>
        )}

        <div className="prose prose-lg max-w-none text-gray-800 prose-headings:font-serif prose-headings:text-acten-green prose-a:text-acten-burgundy" dangerouslySetInnerHTML={{ __html: article.content }}>
        </div>

        <div className="mt-16 pt-8 border-t border-gray-200">
          <Link href="/news" className="inline-flex items-center text-acten-green font-bold hover:text-acten-burgundy transition-colors">
            &larr; Back to all news
          </Link>
        </div>
      </div>
    </div>
  );
}
