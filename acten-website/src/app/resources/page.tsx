import Link from "next/link";
import prisma from "@/lib/prisma";

export default async function ResourcesPage() {
  const resources = await prisma.resource.findMany({
    where: { published: true },
    orderBy: { createdAt: 'desc' },
    include: { category: true }
  });

  return (
    <div className="flex flex-col min-h-screen bg-white">
      <div className="bg-acten-green text-acten-ivory py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="font-serif text-4xl md:text-5xl font-bold mb-4 text-acten-gold">Formation & Resources</h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto">
            Scripture reflections, catechetical materials, and evangelization guides.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {resources.length === 0 ? (
          <div className="text-center py-20 bg-gray-50 rounded-lg">
            <h2 className="text-2xl font-serif text-acten-green mb-2">No Resources Found</h2>
            <p className="text-gray-600">Check back later for new formation materials.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {resources.map((resource) => (
              <div key={resource.id} className="bg-white rounded-lg p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow flex flex-col">
                <div className="flex items-center gap-2 mb-4">
                  <span className="bg-acten-green/10 text-acten-green px-2 py-1 rounded text-xs font-bold uppercase tracking-wider">
                    {resource.type}
                  </span>
                  {resource.category && (
                    <span className="text-xs text-gray-500 uppercase tracking-wider">{resource.category.name}</span>
                  )}
                </div>
                <h3 className="font-serif text-xl font-bold mb-2 text-gray-900">
                  {resource.title}
                </h3>
                <p className="text-gray-600 mb-6 flex-grow">{resource.description}</p>
                <div className="mt-auto">
                  <a href={resource.url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center justify-center w-full px-4 py-2 bg-acten-ivory text-acten-green font-bold rounded hover:bg-acten-green hover:text-white transition-colors">
                    Access Resource
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
