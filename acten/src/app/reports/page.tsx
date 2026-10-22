import Link from 'next/link';
import { FileText, MapPin } from 'lucide-react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Diocesan Reports | ACTEN',
};

export default function ReportsPage() {
  const reports = [
    { id: 1, title: "Annual Evangelization Summary", diocese: "Archdiocese of Abuja", date: "Jan 10, 2026", status: "Published" },
    { id: 2, title: "Prison Ministry Outreach Program", diocese: "Diocese of Awka", date: "Dec 15, 2025", status: "Published" },
    { id: 3, title: "Rural Catechesis Initiative", diocese: "Diocese of Makurdi", date: "Nov 22, 2025", status: "Published" }
  ];

  return (
    <div className="flex flex-col min-h-screen bg-brand-ivory">
      <div className="bg-brand-green py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-serif text-white mb-2">Diocesan Reports</h1>
          <p className="text-brand-gold text-lg">Official activity reports from dioceses and parishes</p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-12 w-full">
        <div className="bg-white p-6 rounded-lg border border-brand-light-grey mb-8 flex justify-between items-center">
          <p className="text-gray-600">Browse verified evangelization reports submitted by authorized representatives.</p>
          <Link href="/submit" className="bg-brand-gold text-brand-green px-4 py-2 rounded font-medium hover:bg-opacity-90">
            Submit a Report
          </Link>
        </div>

        <div className="space-y-4">
          {reports.map((report) => (
            <div key={report.id} className="bg-white p-5 rounded border border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between hover:border-brand-green transition-colors">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-brand-light-grey text-brand-green rounded-full hidden sm:block">
                  <FileText size={20} />
                </div>
                <div>
                  <h3 className="text-lg font-serif text-brand-charcoal mb-1">{report.title}</h3>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-1"><MapPin size={12}/> {report.diocese}</span>
                    <span>{report.date}</span>
                  </div>
                </div>
              </div>
              <button className="mt-4 sm:mt-0 text-sm font-medium text-brand-burgundy hover:underline text-left">
                Read Report
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
