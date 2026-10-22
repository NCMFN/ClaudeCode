"use client";

import { useState } from "react";
import { submitReport } from "@/app/actions";
import Link from "next/link";

export default function SubmitReportPage() {
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const formData = new FormData(event.currentTarget);
    const result = await submitReport(formData);

    if (result.success) {
      setStatus("Report submitted successfully! It is now pending review.");
      (event.target as HTMLFormElement).reset();
    } else {
      setError(result.error || "Failed to submit report.");
    }
  }

  return (
    <div className="bg-white min-h-screen pb-16">
      <div className="bg-acten-charcoal py-16 text-center text-acten-ivory">
        <h1 className="text-4xl font-serif font-bold text-acten-gold mb-4">Submit a Report</h1>
        <p className="text-lg max-w-2xl mx-auto">Share the evangelization activities of your parish or diocese.</p>
      </div>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
        <div className="bg-acten-ivory p-8 rounded-lg shadow-sm border border-gray-100">
          {status && <div className="mb-6 text-green-600 bg-green-50 p-4 rounded border border-green-200 font-bold">{status}</div>}
          {error && <div className="mb-6 text-red-600 bg-red-50 p-4 rounded border border-red-200 font-bold">{error}</div>}

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="title">Report Title</label>
              <input id="title" name="title" type="text" className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-acten-green focus:border-acten-green bg-white" required />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="diocese">Diocese</label>
                <input id="diocese" name="diocese" type="text" className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-acten-green focus:border-acten-green bg-white" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="organizer">Organizer/Parish</label>
                <input id="organizer" name="organizer" type="text" className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-acten-green focus:border-acten-green bg-white" required />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="venue">Venue/Location</label>
              <input id="venue" name="venue" type="text" className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-acten-green focus:border-acten-green bg-white" required />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="content">Full Report</label>
              <textarea id="content" name="content" rows={10} className="w-full border border-gray-300 rounded-md px-4 py-2 focus:ring-acten-green focus:border-acten-green bg-white" required></textarea>
            </div>

            <div className="pt-4 border-t border-gray-200 flex justify-between items-center">
              <Link href="/reports" className="text-acten-green font-medium hover:underline">Cancel</Link>
              <button type="submit" className="bg-acten-burgundy text-white px-6 py-3 rounded-md font-bold hover:bg-opacity-90 transition-colors">
                Submit Report
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
