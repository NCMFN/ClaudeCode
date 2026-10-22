import prisma from "@/lib/prisma";
import EventList from "../../components/EventList";

export default async function EventsPage() {
  const events = await prisma.event.findMany({
    orderBy: { startDate: 'asc' },
    include: { category: true }
  });

  return (
    <div className="flex flex-col min-h-screen bg-white">
      <div className="bg-acten-green text-acten-ivory py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="font-serif text-4xl md:text-5xl font-bold mb-4 text-acten-gold">Activities & Events</h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto">
            Upcoming missions, gatherings, and formation programs.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <EventList events={events} />
      </div>
    </div>
  );
}
