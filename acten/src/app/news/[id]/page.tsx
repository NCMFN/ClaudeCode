import { Metadata } from 'next';
import Link from 'next/link';
import { prisma } from '@/lib/prisma';
import { notFound } from 'next/navigation';

export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  const article = await prisma.article.findUnique({ where: { id: params.id } });
  return {
    title: article ? `${article.title} | ACTEN` : 'Article Not Found',
  };
}

export default async function ArticlePage({ params }: { params: { id: string } }) {
  const article = await prisma.article.findUnique({
    where: { id: params.id },
    include: { author: true }
  });

  if (!article || article.status !== 'Published') {
    notFound();
  }

  return (
    <article className="bg-white min-h-screen pb-16">
      <header className="bg-acten-ivory py-12 border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center space-x-2 text-sm font-bold text-acten-burgundy mb-4 uppercase tracking-wider">
            <span>News</span>
            <span>&bull;</span>
            <span className="text-gray-500 font-normal">
              {article.publishedAt ? new Date(article.publishedAt).toLocaleDateString() : ''}
            </span>
          </div>
          <h1 className="text-3xl md:text-5xl font-serif font-bold text-acten-charcoal mb-6 leading-tight">
            {article.title}
          </h1>
          <div className="flex items-center text-gray-600 text-sm">
            <span>By {article.author?.name || 'ACTEN Editorial Team'}</span>
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-10">
        <div className="aspect-video bg-gray-300 rounded-lg shadow-lg flex items-center justify-center text-gray-500">
          Main Article Image Placeholder
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 prose prose-lg prose-green">
        {article.summary && (
          <p className="lead text-xl text-gray-600 font-medium mb-8">
            {article.summary}
          </p>
        )}
        <div className="whitespace-pre-wrap">{article.content}</div>
      </div>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 pt-8 border-t border-gray-200">
        <Link href="/news" className="text-acten-green font-bold hover:underline">
          &larr; Back to all news
        </Link>
      </div>
    </article>
  );
}
