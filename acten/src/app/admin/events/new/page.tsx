"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createEvent } from "../actions";
import Link from "next/link";

export default function NewEventPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const result = await createEvent(formData);
    if (result.success) {
      router.push("/admin/events");
    } else {
      setError(result.error || "Failed to create event");
    }
  }

  return (
    <div className="max-w-3xl mx-auto bg-white p-8 rounded-lg shadow-sm border border-gray-200">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Create New Event</h2>
        <Link href="/admin/events" className="text-gray-500 hover:underline">Cancel</Link>
      </div>

      {error && <div className="mb-4 text-red-600 bg-red-50 p-3 rounded">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
          <input name="title" type="text" required className="w-full border border-gray-300 rounded-md px-4 py-2" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea name="description" rows={5} required className="w-full border border-gray-300 rounded-md px-4 py-2"></textarea>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input name="startDate" type="datetime-local" required className="w-full border border-gray-300 rounded-md px-4 py-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input name="endDate" type="datetime-local" required className="w-full border border-gray-300 rounded-md px-4 py-2" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Venue</label>
          <input name="venue" type="text" className="w-full border border-gray-300 rounded-md px-4 py-2" />
        </div>

        <div className="flex items-center space-x-2">
          <input name="isOnline" type="checkbox" id="isOnline" value="true" className="rounded border-gray-300 text-acten-green focus:ring-acten-green" />
          <label htmlFor="isOnline" className="text-sm font-medium text-gray-700">This is an online event</label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select name="status" className="w-full border border-gray-300 rounded-md px-4 py-2">
            <option value="Upcoming">Upcoming</option>
            <option value="Ongoing">Ongoing</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>

        <button type="submit" className="bg-acten-green text-white px-6 py-2 rounded-md font-bold hover:bg-opacity-90">
          Save Event
        </button>
      </form>
    </div>
  );
}
