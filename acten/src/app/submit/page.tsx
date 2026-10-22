"use client";

import { useState } from 'react';
import { Send, CheckCircle2, AlertCircle } from 'lucide-react';

export default function SubmitReportPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    const formData = new FormData(e.currentTarget);
    const data = Object.fromEntries(formData.entries());

    try {
      const res = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        throw new Error('Failed to submit report.');
      }
      setIsSuccess(true);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen bg-brand-ivory flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-sm text-center border border-brand-light-grey">
          <CheckCircle2 size={64} className="mx-auto text-brand-green mb-6" />
          <h2 className="text-2xl font-serif text-brand-charcoal mb-2">Report Submitted</h2>
          <p className="text-gray-600 mb-6">
            Thank you for sharing this evangelization activity. Your report has been securely submitted and is pending editorial review.
          </p>
          <button
            onClick={() => setIsSuccess(false)}
            className="text-brand-green font-medium hover:underline"
          >
            Submit another report
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-brand-ivory">
      <div className="bg-brand-green py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-serif text-white mb-2">Submit a Report</h1>
          <p className="text-brand-gold text-lg">Document evangelization activities from your parish or diocese.</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-12 w-full">
        <div className="bg-white p-8 rounded-lg shadow-sm border border-brand-light-grey">

          <div className="mb-8 p-4 bg-amber-50 border border-amber-200 rounded text-amber-800 text-sm">
            <h4 className="font-bold flex items-center gap-2 mb-1"><AlertCircle size={16}/> Important Notice</h4>
            <p>All submitted reports undergo an editorial review process before publication. Please ensure facts, dates, and locations are accurate. Do not include sensitive or unverified information.</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 text-red-700 border border-red-200 rounded text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Submitter Details */}
            <section>
              <h3 className="text-lg font-serif text-brand-green border-b pb-2 mb-4">Submitter Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                  <input required name="submitterName" type="text" className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Contact Email *</label>
                  <input required name="contactEmail" type="email" className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Diocese / Organization</label>
                  <input name="diocese" type="text" className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Parish</label>
                  <input name="parish" type="text" className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none" />
                </div>
              </div>
            </section>

            {/* Activity Details */}
            <section>
              <h3 className="text-lg font-serif text-brand-green border-b pb-2 mb-4">Activity Details</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Report Headline / Title *</label>
                  <input required name="title" type="text" className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none" placeholder="e.g., Lenten Mission in St. Paul Parish" />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Date of Activity *</label>
                    <input required name="activityDate" type="date" className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Location / State</label>
                    <input name="location" type="text" className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none" />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Brief Summary * (Max 200 chars)</label>
                  <textarea required name="summary" rows={2} maxLength={200} className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none"></textarea>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Report *</label>
                  <textarea required name="content" rows={8} className="w-full p-2 border border-gray-300 rounded focus:border-brand-green outline-none" placeholder="Provide the full details of the evangelization activity..."></textarea>
                </div>
              </div>
            </section>

            {/* Declarations */}
            <section className="bg-gray-50 p-4 rounded border border-gray-200 text-sm text-gray-700">
              <label className="flex items-start gap-3 cursor-pointer">
                <input required type="checkbox" className="mt-1" />
                <span>I confirm that the information provided is accurate and I have the authority to submit this report on behalf of the organizing body.</span>
              </label>
            </section>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-brand-green text-white py-3 rounded font-medium hover:bg-opacity-90 transition-colors flex justify-center items-center gap-2 disabled:opacity-50"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Report'} <Send size={18} />
            </button>
          </form>

        </div>
      </div>
    </div>
  );
}
