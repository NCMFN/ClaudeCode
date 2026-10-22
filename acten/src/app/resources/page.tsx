import { FileText, Download, Play, Link as LinkIcon, Search } from 'lucide-react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Formation & Resources | ACTEN',
  description: 'Catholic evangelization materials, catechetical resources, and scripture reflections.',
};

export default function ResourcesPage() {
  const resources = [
    { id: 1, title: "Guidelines for Parish Missions", type: "PDF", category: "Evangelization Guides", icon: FileText },
    { id: 2, title: "Defending the Faith: Basic Apologetics", type: "VIDEO", category: "Training", icon: Play },
    { id: 3, title: "Sunday Scripture Reflections (Year A)", type: "ARTICLE", category: "Scripture", icon: FileText },
    { id: 4, title: "Vatican Document on Evangelization", type: "LINK", category: "Church Documents", icon: LinkIcon },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-brand-ivory">
      <div className="bg-brand-green py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-serif text-white mb-2">Formation & Resources</h1>
          <p className="text-brand-gold text-lg">Approved Catholic evangelization materials and guides</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12 w-full">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-brand-light-grey mb-8 flex gap-2">
          <div className="relative flex-grow">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search resources, reflections, or guidelines..."
              className="w-full pl-10 pr-4 py-2 border rounded focus:outline-none focus:border-brand-green"
            />
          </div>
          <button className="bg-brand-green text-white px-6 py-2 rounded hover:bg-opacity-90 font-medium">Search</button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resources.map((res) => {
            const Icon = res.icon;
            return (
              <div key={res.id} className="bg-white p-6 rounded-lg border border-brand-light-grey hover:border-brand-gold transition-colors flex flex-col group">
                <div className="flex items-center gap-3 mb-4 text-brand-green">
                  <div className="p-2 bg-brand-ivory rounded group-hover:bg-brand-gold group-hover:text-white transition-colors">
                    <Icon size={24} />
                  </div>
                  <span className="text-xs font-bold uppercase tracking-wider text-brand-burgundy">{res.category}</span>
                </div>
                <h3 className="text-xl font-serif text-brand-charcoal mb-4">{res.title}</h3>
                <div className="mt-auto flex justify-between items-center pt-4 border-t border-gray-100">
                  <span className="text-xs text-gray-500 font-medium bg-gray-100 px-2 py-1 rounded">{res.type}</span>
                  <button className="text-sm font-medium text-brand-green flex items-center gap-1 hover:text-brand-gold">
                    Access Resource <Download size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
