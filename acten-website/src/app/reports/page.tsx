import Link from "next/link";
import prisma from "@/lib/prisma";

export default async function ReportsPage() {
  const reports = await prisma.report.findMany({
    where: { status: "APPROVED" },
    orderBy: { createdAt: 'desc' }
  });

  return (
    <div className="flex flex-col min-h-screen bg-white">
      <div className="bg-acten-green text-acten-ivory py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="font-serif text-4xl md:text-5xl font-bold mb-4 text-acten-gold">Diocesan Reports</h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto mb-8">
            Archive of evangelization activities across Nigerian Catholic communities.
          </p>
          <Link href="/reports/submit" className="inline-block px-6 py-3 bg-acten-gold text-acten-green font-bold rounded-md hover:bg-yellow-600 transition-colors">
            Submit a Report
          </Link>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {reports.length === 0 ? (
          <div className="text-center py-20 bg-gray-50 rounded-lg">
            <h2 className="text-2xl font-serif text-acten-green mb-2">No Reports Published</h2>
            <p className="text-gray-600">Reports submitted by dioceses will appear here once approved.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {reports.map((report) => (
              <div key={report.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-serif text-xl font-bold mb-1">
                      <Link href={`/reports/${report.slug}`} className="hover:text-acten-burgundy">{report.title}</Link>
                    </h3>
                    <div className="text-sm text-gray-500 font-medium">
                      {report.diocese && <span>{report.diocese} Diocese</span>}
                      {report.parish && <span> • {report.parish}</span>}
                    </div>
                  </div>
                  {report.date && (
                    <div className="bg-acten-ivory px-3 py-1 rounded border border-gray-200 text-xs font-bold text-acten-green whitespace-nowrap">
                      {new Date(report.date).toLocaleDateString()}
                    </div>
                  )}
                </div>
                <p className="text-gray-600 mb-4 line-clamp-3">{report.summary || report.content.substring(0, 150) + '...'}</p>
                <Link href={`/reports/${report.slug}`} className="text-acten-green font-bold hover:text-acten-burgundy text-sm">
                  Read Full Report &rarr;
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
