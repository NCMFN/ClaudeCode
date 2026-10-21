import { Metadata } from 'next';
import { prisma } from '@/lib/prisma';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Diocesan Reports | ACTEN',
  description: 'Archive of evangelization activity reports across Nigerian Catholic communities.',
};



export default async function ReportsPage() {
  const reports = await prisma.report.findMany({
    where: { status: 'Approved' },
    orderBy: { date: 'desc' },
  });

  return (
    <div className="bg-acten-ivory min-h-screen pb-16">
      <div className="bg-acten-green py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-serif font-bold text-white mb-2">Diocesan Reports</h1>
          <p className="text-acten-gold">Verified archives of evangelization activities</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
        <div className="bg-white p-6 rounded-lg shadow-sm mb-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-600 mb-4 md:mb-0">Showing verified reports from participating dioceses.</p>
          <Link href="/contact" className="bg-acten-burgundy text-white px-6 py-2 rounded-md font-bold hover:bg-opacity-90 inline-block text-center">
            Submit a Report
          </Link>
        </div>

        {reports.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow-sm text-center">
            <p className="text-gray-500">No approved reports available at the moment.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {reports.map((report) => (
              <div key={report.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className="text-xs font-bold text-acten-green uppercase tracking-wider">{report.diocese}</span>
                    <h3 className="text-xl font-bold mt-1 text-acten-charcoal">{report.title}</h3>
                  </div>
                  <span className="text-sm text-gray-500">{new Date(report.date).toLocaleDateString()}</span>
                </div>
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {report.summary || report.content}
                </p>
                <div className="text-sm text-gray-500 mb-4">
                  <strong>Organizer:</strong> {report.organizer || 'N/A'} <br/>
                  <strong>Venue:</strong> {report.venue || 'N/A'}
                </div>
                {/* For now, just a button, but ideally links to a detail page */}
                <button className="text-acten-burgundy font-bold text-sm hover:underline">Read Full Report &rarr;</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
