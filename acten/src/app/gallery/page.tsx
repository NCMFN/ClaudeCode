import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Gallery | ACTEN',
  description: 'Photographs and videos from Catholic evangelization activities across Nigeria.',
};

export default function GalleryPage() {
  return (
    <div className="bg-white min-h-screen pb-16">
      <div className="bg-acten-charcoal py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-3xl font-serif font-bold text-acten-gold mb-2">Media Gallery</h1>
          <p className="text-acten-ivory">Glimpses of faith in action across Nigerian communities</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
        <div className="flex flex-wrap justify-center gap-4 mb-10">
          <button className="px-4 py-2 bg-acten-green text-white rounded-full text-sm font-medium">All Media</button>
          <button className="px-4 py-2 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded-full text-sm font-medium">2023 Events</button>
          <button className="px-4 py-2 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded-full text-sm font-medium">Parish Missions</button>
          <button className="px-4 py-2 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded-full text-sm font-medium">Youth Outreaches</button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="group relative aspect-square bg-gray-200 rounded-lg overflow-hidden shadow-sm cursor-pointer">
              <div className="absolute inset-0 flex items-center justify-center text-gray-400">Image {i}</div>
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-60 transition-opacity duration-300 flex flex-col justify-end p-4">
                <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 transform translate-y-4 group-hover:translate-y-0">
                  <h4 className="text-white font-bold text-sm">Evangelization Event {i}</h4>
                  <p className="text-gray-300 text-xs mt-1">Location, State</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <button className="bg-transparent border-2 border-acten-green text-acten-green px-8 py-3 rounded-md font-bold hover:bg-acten-green hover:text-white transition-colors">
            Load More Media
          </button>
        </div>
      </div>
    </div>
  );
}
