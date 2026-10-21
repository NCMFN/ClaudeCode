import { Metadata } from 'next';
import Link from 'next/link';
import { prisma } from '@/lib/prisma';
import { notFound } from 'next/navigation';

export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  const event = await prisma.event.findUnique({ where: { id: params.id } });
  return {
    title: event ? `${event.title} | ACTEN` : 'Event Not Found',
  };
}

export default async function EventDetailPage({ params }: { params: { id: string } }) {
  const event = await prisma.event.findUnique({ where: { id: params.id } });

  if (!event || event.status !== 'Upcoming') {
    notFound();
  }

  const startDate = new Date(event.startDate);
  const endDate = new Date(event.endDate);

  return (
    <div className="bg-white min-h-screen pb-16">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
        <Link href="/events" className="text-acten-green font-bold hover:underline mb-6 inline-block">
          &larr; Back to Events
        </Link>

        <div className="bg-acten-ivory rounded-xl overflow-hidden shadow-sm border border-gray-100">
          <div className="h-64 bg-gray-300 flex items-center justify-center">
            Event Banner Placeholder
          </div>

          <div className="p-8 md:p-12">
            <div className="flex items-center space-x-2 text-sm font-bold text-acten-burgundy mb-4 uppercase tracking-wider">
              <span>{event.isOnline ? 'Online' : 'In Person'}</span>
              <span>&bull;</span>
              <span className="text-green-600">Upcoming</span>
            </div>

            <h1 className="text-3xl md:text-4xl font-serif font-bold text-acten-charcoal mb-6">
              {event.title}
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8 border-y border-gray-200 py-8">
              <div>
                <h4 className="text-gray-500 font-bold text-sm uppercase mb-1">Date & Time</h4>
                <p className="font-medium">{startDate.toLocaleDateString()}</p>
                <p className="text-sm text-gray-600">
                  {startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} -
                  {endDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
              <div>
                <h4 className="text-gray-500 font-bold text-sm uppercase mb-1">Location</h4>
                <p className="font-medium">{event.isOnline ? 'Online Event' : event.venue}</p>
              </div>
              <div>
                <h4 className="text-gray-500 font-bold text-sm uppercase mb-1">Organizer</h4>
                <p className="font-medium">ACTEN National Team</p>
              </div>
            </div>

            <div className="prose prose-lg prose-green max-w-none">
              <h3 className="font-serif text-acten-green">About this Event</h3>
              <div className="whitespace-pre-wrap">{event.description}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
