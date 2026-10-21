"use client";

import { useMemo } from "react";
import Link from "next/link";
import { Event, Category } from "@prisma/client";

type EventWithCategory = Event & { category: Category | null };

export default function EventList({ events }: { events: EventWithCategory[] }) {
  const { upcomingEvents, pastEvents } = useMemo(() => {
    const now = new Date();
    return {
      upcomingEvents: events.filter(e => new Date(e.endDate) >= now),
      pastEvents: events.filter(e => new Date(e.endDate) < now)
    };
  }, [events]);

  return (
    <>
      <h2 className="font-serif text-3xl font-bold text-acten-green mb-8 border-b pb-2">Upcoming Events</h2>

      {upcomingEvents.length === 0 ? (
        <div className="text-center py-16 bg-acten-ivory/50 rounded-lg border border-gray-100 mb-16">
          <p className="text-gray-600 text-lg">There are currently no upcoming events scheduled.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {upcomingEvents.map((event) => (
            <div key={event.id} className="bg-white rounded-lg overflow-hidden shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="relative h-48 bg-gray-200">
                {event.imageUrl ? (
                  <img src={event.imageUrl} alt={event.title} className="w-full h-full object-cover" />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center text-gray-400">Event Image</div>
                )}
                <div className="absolute top-4 right-4 bg-white/90 px-3 py-1 rounded text-center shadow">
                  <div className="text-acten-burgundy font-bold text-xl leading-none">{new Date(event.startDate).getDate()}</div>
                  <div className="text-gray-600 text-xs font-medium uppercase tracking-wider">{new Date(event.startDate).toLocaleDateString('en-US', { month: 'short' })}</div>
                </div>
              </div>
              <div className="p-6">
                <div className="flex items-center gap-2 mb-2">
                  {event.category && (
                    <span className="text-xs font-bold uppercase tracking-wider text-acten-green">{event.category.name}</span>
                  )}
                </div>
                <h3 className="font-serif text-xl font-bold mb-2">
                  {event.title}
                </h3>
                <div className="space-y-2 mb-4 text-sm text-gray-600">
                  <div className="flex items-start gap-2">
                    <svg className="w-5 h-5 text-gray-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <span>
                      {new Date(event.startDate).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} -
                      {new Date(event.endDate).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </span>
                  </div>
                  <div className="flex items-start gap-2">
                    <svg className="w-5 h-5 text-gray-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                    <span>{event.venue || 'TBA'}, {event.state || ''}</span>
                  </div>
                </div>
                <p className="text-gray-600 text-sm line-clamp-2 mb-4">{event.description}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {pastEvents.length > 0 && (
        <>
          <h2 className="font-serif text-2xl font-bold text-gray-800 mb-8 border-b pb-2">Past Events</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 opacity-75">
            {pastEvents.map((event) => (
              <div key={event.id} className="bg-gray-50 rounded-lg p-4 border border-gray-100 flex gap-4">
                <div className="bg-white p-2 rounded border border-gray-200 text-center min-w-[60px] h-fit">
                  <div className="text-gray-500 font-bold leading-none">{new Date(event.startDate).getDate()}</div>
                  <div className="text-gray-400 text-xs">{new Date(event.startDate).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}</div>
                </div>
                <div>
                  <h3 className="font-bold text-gray-800 text-sm">{event.title}</h3>
                  <p className="text-xs text-gray-500 mt-1">{event.venue}, {event.state}</p>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </>
  );
}
