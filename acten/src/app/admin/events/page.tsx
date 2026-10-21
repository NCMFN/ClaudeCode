import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { deleteEvent } from "./actions";



export default async function AdminEventsPage() {
  const events = await prisma.event.findMany({
    orderBy: { startDate: "desc" },
  });

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Manage Events</h2>
        <Link href="/admin/events/new" className="bg-acten-green text-white px-4 py-2 rounded-md hover:bg-opacity-90">
          Add New Event
        </Link>
      </div>
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Event Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200 text-gray-900">
            {events.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center text-gray-500">No events found.</td>
              </tr>
            )}
            {events.map((event) => (
              <tr key={event.id}>
                <td className="px-6 py-4 whitespace-nowrap">{event.title}</td>
                <td className="px-6 py-4 whitespace-nowrap">{new Date(event.startDate).toLocaleDateString()}</td>
                <td className="px-6 py-4 whitespace-nowrap">{event.isOnline ? 'Online' : event.venue}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded-full text-xs ${event.status === 'Upcoming' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                    {event.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium flex justify-end space-x-3">
                  <Link href={`/admin/events/${event.id}/edit`} className="text-acten-green hover:underline">Edit</Link>
                  <form action={async () => {
                    "use server";
                    await deleteEvent(event.id);
                  }}>
                    <button type="submit" className="text-red-600 hover:underline">Delete</button>
                  </form>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
