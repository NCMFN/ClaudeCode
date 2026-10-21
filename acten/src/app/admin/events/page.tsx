import { Plus, Search, Edit, Trash2 } from 'lucide-react';

export default function AdminEvents() {
  const events = [
    { id: 1, title: "National Catholic Evangelizers Convention", date: "Oct 12, 2026", venue: "Abuja", status: "Upcoming" },
    { id: 2, title: "Digital Apologetics Seminar", date: "Jul 24, 2026", venue: "Online", status: "Upcoming" },
    { id: 3, title: "Lagos Youth Mission", date: "Jan 10, 2026", venue: "Lagos", status: "Completed" },
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-serif text-brand-charcoal">Manage Events</h1>
        <button className="bg-brand-green text-white px-4 py-2 rounded font-medium flex items-center gap-2 hover:bg-opacity-90">
          <Plus size={18} /> New Event
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              placeholder="Search events..."
              className="w-full pl-9 pr-4 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:border-brand-green"
            />
          </div>
        </div>

        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white border-b text-sm text-gray-500">
              <th className="p-4 font-medium">Event Title</th>
              <th className="p-4 font-medium">Date</th>
              <th className="p-4 font-medium">Venue</th>
              <th className="p-4 font-medium">Status</th>
              <th className="p-4 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={event.id} className="border-b hover:bg-gray-50 transition-colors">
                <td className="p-4 font-medium text-gray-800">{event.title}</td>
                <td className="p-4 text-sm text-gray-600">{event.date}</td>
                <td className="p-4 text-sm text-gray-600">{event.venue}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    event.status === 'Upcoming' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {event.status}
                  </span>
                </td>
                <td className="p-4 text-right">
                  <div className="flex justify-end gap-3 text-gray-400">
                    <button className="hover:text-brand-green"><Edit size={16} /></button>
                    <button className="hover:text-red-500"><Trash2 size={16} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
