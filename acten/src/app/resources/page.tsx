import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Formation & Resources | ACTEN',
  description: 'Searchable library of Catholic teaching materials, evangelization guides, and training resources.',
};

export default function ResourcesPage() {
  return (
    <div className="bg-acten-ivory min-h-screen pb-16">
      <div className="bg-acten-green py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-3xl font-serif font-bold text-white mb-4">Formation & Resources</h1>
          <p className="text-acten-gold max-w-2xl mx-auto">Access articles, catechetical materials, and evangelization guides to support your ministry.</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
        {/* Search and Filters */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <input type="text" placeholder="Search resources..." className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-acten-green focus:border-acten-green bg-white" />
            </div>
            <div>
              <select className="w-full border border-gray-300 rounded-md px-4 py-2 bg-white">
                <option>All Types</option>
                <option>PDF Documents</option>
                <option>Articles</option>
                <option>Videos</option>
              </select>
            </div>
            <div>
              <button className="w-full bg-acten-gold text-acten-charcoal font-bold rounded-md px-4 py-2 hover:bg-acten-green hover:text-white transition-colors">
                Search
              </button>
            </div>
          </div>
        </div>

        {/* Resource List */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex flex-col h-full hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-2 text-xs font-bold text-acten-burgundy mb-3 uppercase tracking-wider">
                <span className="bg-red-50 text-acten-burgundy px-2 py-1 rounded">PDF Document</span>
              </div>
              <h3 className="text-lg font-bold text-acten-charcoal mb-2">Guide to Parish Evangelization Vol. {i}</h3>
              <p className="text-sm text-gray-600 mb-4 flex-grow">
                A comprehensive guide detailing strategies and best practices for establishing an effective evangelization team within your parish.
              </p>
              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <span className="text-xs text-gray-500">Added: Sep {i}, 2023</span>
                <button className="text-acten-green font-bold text-sm hover:underline">Download &darr;</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
