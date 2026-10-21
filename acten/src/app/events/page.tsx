import { Metadata } from 'next';
import Link from 'next/link';
import { prisma } from '@/lib/prisma';

export const metadata: Metadata = {
  title: 'Activities & Events | ACTEN',
  description: 'Upcoming Catholic evangelization events, training programmes, and missions across Nigeria.',
};



export default async function EventsPage() {
  const events = await prisma.event.findMany({
    where: { status: 'Upcoming' },
    orderBy: { startDate: 'asc' },
  });

  return (
    <div className="bg-white min-h-screen pb-16">
      <div className="bg-acten-charcoal py-16 text-center text-acten-ivory">
        <h1 className="text-4xl font-serif font-bold text-acten-gold mb-4">Activities & Events</h1>
        <p className="text-lg max-w-2xl mx-auto">Discover upcoming missions, training programmes, and Catholic gatherings.</p>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
        <div className="mb-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex space-x-2">
            <button className="px-4 py-2 bg-acten-green text-white rounded-md text-sm font-medium">Upcoming</button>
            <button className="px-4 py-2 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded-md text-sm font-medium">Past Events</button>
          </div>
        </div>

        {events.length === 0 ? (
          <div className="bg-acten-ivory p-8 rounded-lg shadow-sm text-center border border-gray-100">
            <p className="text-gray-500">No upcoming events at this time.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {events.map((event) => {
              const date = new Date(event.startDate);
              return (
                <div key={event.id} className="flex flex-col md:flex-row bg-acten-ivory rounded-lg overflow-hidden shadow-sm border border-gray-100">
                  <div className="md:w-1/4 bg-acten-burgundy text-white flex flex-col items-center justify-center py-6 px-4">
                    <span className="text-sm font-bold uppercase tracking-widest">
                      {date.toLocaleString('default', { month: 'short' })}
                    </span>
                    <span className="text-4xl font-bold my-1">{date.getDate()}</span>
                    <span className="text-sm">{date.getFullYear()}</span>
                  </div>
                  <div className="p-6 md:w-3/4 flex flex-col justify-center">
                    <div className="flex items-center space-x-2 text-xs font-bold text-gray-500 mb-2 uppercase">
                      <span>{event.isOnline ? 'Online' : event.venue}</span>
                    </div>
                    <h3 className="text-2xl font-serif font-bold text-acten-charcoal mb-2">
                      <Link href={`/events/${event.id}`} className="hover:text-acten-green">
                        {event.title}
                      </Link>
                    </h3>
                    <p className="text-gray-600 mb-4 line-clamp-2">
                      {event.description}
                    </p>
                    <div className="flex items-center justify-between mt-auto">
                      <span className="text-sm text-gray-500 font-medium">Organizer: ACTEN</span>
                      <Link href={`/events/${event.id}`} className="bg-acten-green text-white px-4 py-2 rounded-md text-sm font-bold hover:bg-opacity-90">
                        View Details
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
