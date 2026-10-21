import Link from "next/link";
import prisma from "@/lib/prisma";

export default async function GalleryPage() {
  const albums = await prisma.galleryAlbum.findMany({
    orderBy: { createdAt: 'desc' },
    include: { _count: { select: { images: true } } }
  });

  return (
    <div className="flex flex-col min-h-screen bg-white">
      <div className="bg-acten-green text-acten-ivory py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="font-serif text-4xl md:text-5xl font-bold mb-4 text-acten-gold">Gallery</h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto">
            Visual documentation of evangelization activities across Nigeria.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {albums.length === 0 ? (
          <div className="text-center py-20 bg-gray-50 rounded-lg">
            <h2 className="text-2xl font-serif text-acten-green mb-2">No Albums Found</h2>
            <p className="text-gray-600">Check back later for new photos.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {albums.map((album) => (
              <Link href={`/gallery/${album.slug}`} key={album.id} className="group">
                <div className="bg-white rounded-lg overflow-hidden shadow-sm border border-gray-100 hover:shadow-md transition-all">
                  <div className="relative h-64 bg-gray-200 overflow-hidden">
                    {album.coverImage ? (
                      <img src={album.coverImage} alt={album.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center text-gray-400">Album Cover</div>
                    )}
                    <div className="absolute bottom-4 right-4 bg-black/70 text-white px-2 py-1 rounded text-xs font-bold flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                      {album._count.images}
                    </div>
                  </div>
                  <div className="p-4">
                    <h3 className="font-serif text-xl font-bold mb-1 group-hover:text-acten-burgundy transition-colors">{album.title}</h3>
                    <p className="text-sm text-gray-500">{album.date ? new Date(album.date).toLocaleDateString() : 'Various Dates'}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
