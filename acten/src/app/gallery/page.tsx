import { Image as ImageIcon } from 'lucide-react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Gallery | ACTEN',
  description: 'Photographs and videos from Catholic evangelization activities.',
};

export default function GalleryPage() {
  const albums = [
    { id: 1, title: "Lenten Rural Mission", count: 24, location: "Abuja" },
    { id: 2, title: "Youth Evangelizers Training", count: 45, location: "Lagos" },
    { id: 3, title: "National Convention 2025", count: 120, location: "Enugu" },
    { id: 4, title: "Street Evangelism Outreach", count: 18, location: "Port Harcourt" },
    { id: 5, title: "Diocesan Rally", count: 56, location: "Kaduna" },
    { id: 6, title: "Hospital Visitation Ministry", count: 12, location: "Ibadan" }
  ];

  return (
    <div className="flex flex-col min-h-screen bg-brand-ivory">
      <div className="bg-brand-green py-12 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl font-serif text-white mb-2">Media Gallery</h1>
          <p className="text-brand-gold text-lg">Visual records of our evangelization activities</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12 w-full">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {albums.map((album) => (
            <div key={album.id} className="bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-md border border-brand-light-grey cursor-pointer group">
              <div className="aspect-video bg-gray-200 flex items-center justify-center relative overflow-hidden">
                <ImageIcon size={48} className="text-gray-400 group-hover:scale-110 transition-transform duration-300" />
                <div className="absolute inset-0 bg-brand-green bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300" />
              </div>
              <div className="p-4">
                <h3 className="font-serif text-lg text-brand-charcoal mb-1">{album.title}</h3>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>{album.location}</span>
                  <span>{album.count} photos</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
