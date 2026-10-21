import { Calendar as CalendarIcon, MapPin, Clock } from 'lucide-react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Activities & Events | ACTEN',
  description: 'Upcoming Catholic evangelization activities, missions, and formation events.',
};

export default function EventsPage() {
  const events = [
    {
      id: "1",
      title: "National Catholic Evangelizers Convention",
      date: "October 12-15, 2026",
      time: "9:00 AM - 5:00 PM Daily",
      venue: "Catholic Secretariat of Nigeria, Abuja",
      organizer: "ACTEN National Executive",
      status: "UPCOMING",
      description: "Annual gathering of all trained evangelizers for spiritual renewal, theological formation, and strategic planning for national outreach."
    },
    {
      id: "2",
      title: "Digital Apologetics Seminar",
      date: "July 24, 2026",
      time: "10:00 AM - 2:00 PM",
      venue: "Online (Zoom)",
      organizer: "Digital Evangelization Team",
      status: "UPCOMING",
      description: "A specialized training session on defending the faith online and using social media as a tool for effective Catholic evangelization."
    }
  ];

  return (
    <div className="flex flex-col min-h-screen bg-brand-ivory">
      <div className="bg-brand-green py-12 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl font-serif text-white mb-2">Activities & Events</h1>
          <p className="text-brand-gold text-lg">Upcoming missions, conventions, and formation programmes</p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-12 w-full">

        {/* Filters bar */}
        <div className="bg-white p-4 rounded-lg shadow-sm border border-brand-light-grey mb-8 flex flex-wrap gap-4 items-center justify-between">
          <div className="flex gap-2">
            <select className="p-2 border rounded bg-white text-sm outline-none focus:border-brand-green">
              <option>All Event Types</option>
              <option>Conventions</option>
              <option>Seminars</option>
              <option>Missions</option>
            </select>
            <select className="p-2 border rounded bg-white text-sm outline-none focus:border-brand-green">
              <option>All Locations</option>
              <option>Abuja</option>
              <option>Lagos</option>
              <option>Online</option>
            </select>
          </div>
          <div className="text-sm text-gray-500 font-medium">
            Showing {events.length} upcoming events
          </div>
        </div>

        <div className="space-y-6">
          {events.map(event => (
            <div key={event.id} className="bg-white rounded-lg border border-brand-light-grey overflow-hidden flex flex-col md:flex-row hover:shadow-md transition-shadow">

              {/* Date Box */}
              <div className="bg-brand-light-grey text-brand-green md:w-48 p-6 flex flex-col items-center justify-center border-b md:border-b-0 md:border-r border-gray-200">
                <CalendarIcon size={32} className="mb-2 text-brand-gold" />
                <span className="text-center font-bold text-sm leading-tight">{event.date}</span>
                <span className="text-xs text-gray-500 mt-2 bg-white px-2 py-1 rounded-full border">{event.status}</span>
              </div>

              {/* Details */}
              <div className="p-6 flex-grow flex flex-col">
                <h2 className="text-2xl font-serif text-brand-charcoal mb-2">{event.title}</h2>
                <p className="text-gray-600 text-sm mb-4">{event.description}</p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-gray-600 mt-auto bg-brand-ivory p-4 rounded">
                  <div className="flex items-center gap-2">
                    <Clock size={16} className="text-brand-burgundy" />
                    <span>{event.time}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin size={16} className="text-brand-burgundy" />
                    <span>{event.venue}</span>
                  </div>
                </div>
              </div>

            </div>
          ))}

          {events.length === 0 && (
            <div className="text-center p-12 bg-white rounded-lg border border-dashed border-gray-300">
              <p className="text-gray-500">No upcoming events currently scheduled.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
