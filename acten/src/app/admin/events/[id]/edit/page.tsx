import { prisma } from "@/lib/prisma";
import { updateEvent } from "../../actions";
import Link from "next/link";
import { redirect } from "next/navigation";

export default async function EditEventPage({ params }: { params: { id: string } }) {
  const event = await prisma.event.findUnique({ where: { id: params.id } });

  if (!event) {
    return <div>Event not found</div>;
  }

  // Format dates for datetime-local input
  const formatForInput = (date: Date) => {
    return date.toISOString().slice(0, 16);
  };

  async function handleSubmit(formData: FormData) {
    "use server";
    const result = await updateEvent(params.id, formData);
    if (result.success) {
      redirect("/admin/events");
    }
  }

  return (
    <div className="max-w-3xl mx-auto bg-white p-8 rounded-lg shadow-sm border border-gray-200">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Edit Event</h2>
        <Link href="/admin/events" className="text-gray-500 hover:underline">Cancel</Link>
      </div>

      <form action={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
          <input name="title" type="text" defaultValue={event.title} required className="w-full border border-gray-300 rounded-md px-4 py-2" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea name="description" rows={5} defaultValue={event.description} required className="w-full border border-gray-300 rounded-md px-4 py-2"></textarea>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input name="startDate" type="datetime-local" defaultValue={formatForInput(event.startDate)} required className="w-full border border-gray-300 rounded-md px-4 py-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input name="endDate" type="datetime-local" defaultValue={formatForInput(event.endDate)} required className="w-full border border-gray-300 rounded-md px-4 py-2" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Venue</label>
          <input name="venue" type="text" defaultValue={event.venue || ""} className="w-full border border-gray-300 rounded-md px-4 py-2" />
        </div>

        <div className="flex items-center space-x-2">
          <input name="isOnline" type="checkbox" id="isOnline" value="true" defaultChecked={event.isOnline} className="rounded border-gray-300 text-acten-green focus:ring-acten-green" />
          <label htmlFor="isOnline" className="text-sm font-medium text-gray-700">This is an online event</label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select name="status" defaultValue={event.status} className="w-full border border-gray-300 rounded-md px-4 py-2">
            <option value="Upcoming">Upcoming</option>
            <option value="Ongoing">Ongoing</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>

        <button type="submit" className="bg-acten-green text-white px-6 py-2 rounded-md font-bold hover:bg-opacity-90">
          Update Event
        </button>
      </form>
    </div>
  );
}
