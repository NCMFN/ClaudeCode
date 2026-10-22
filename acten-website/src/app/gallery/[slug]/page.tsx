import Link from "next/link";
import prisma from "@/lib/prisma";
import { notFound } from "next/navigation";

export default async function AlbumPage({ params }: { params: { slug: string } }) {
  const album = await prisma.galleryAlbum.findUnique({
    where: { slug: params.slug },
    include: { images: true }
  });

  if (!album) {
    notFound();
  }

  return (
    <div className="flex flex-col min-h-screen bg-white">
      <div className="bg-acten-green text-acten-ivory py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Link href="/gallery" className="text-acten-gold text-sm font-bold tracking-wider uppercase mb-4 inline-block hover:underline">&larr; Back to Gallery</Link>
          <h1 className="font-serif text-3xl md:text-5xl font-bold mb-4 text-white">{album.title}</h1>
          <p className="text-lg text-acten-ivory/80 max-w-2xl mx-auto">
            {album.description || 'Evangelization visual documentation.'}
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {album.images.length === 0 ? (
          <p className="text-center text-gray-500 py-12">No images in this album yet.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {album.images.map((image) => (
              <div key={image.id} className="relative group aspect-square bg-gray-200 overflow-hidden rounded-lg">
                <img src={image.url} alt={image.caption || album.title} className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110" />
                {image.caption && (
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                    <p className="text-white text-sm">{image.caption}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
