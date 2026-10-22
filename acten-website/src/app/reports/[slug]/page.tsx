import Link from "next/link";
import prisma from "@/lib/prisma";
import { notFound } from "next/navigation";

export default async function ReportPage({ params }: { params: { slug: string } }) {
  const report = await prisma.report.findUnique({
    where: { slug: params.slug },
    include: { submitter: true }
  });

  if (!report || report.status !== "APPROVED") {
    notFound();
  }

  return (
    <div className="flex flex-col min-h-screen bg-white">
      <div className="bg-acten-green text-acten-ivory py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <Link href="/reports" className="text-acten-gold text-sm font-bold tracking-wider uppercase mb-4 inline-block hover:underline">&larr; Back to Reports</Link>
          <h1 className="font-serif text-3xl md:text-5xl font-bold mb-6 text-white leading-tight">
            {report.title}
          </h1>
          <div className="flex flex-wrap items-center gap-y-2 gap-x-6 text-sm text-acten-ivory/80">
            {report.date && (
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                {new Date(report.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
              </div>
            )}
            {(report.diocese || report.parish) && (
              <div className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                {report.diocese && <span>{report.diocese}</span>}
                {report.diocese && report.parish && <span>, </span>}
                {report.parish && <span>{report.parish}</span>}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {report.summary && (
          <div className="mb-10 text-xl text-gray-600 font-serif italic border-l-4 border-acten-gold pl-6 py-2 bg-gray-50">
            {report.summary}
          </div>
        )}

        <div className="prose prose-lg max-w-none text-gray-800" dangerouslySetInnerHTML={{ __html: report.content }}>
        </div>

        {report.organizer && (
          <div className="mt-12 p-6 bg-acten-ivory rounded-lg border border-gray-200">
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-2">Organizer / Team</h3>
            <p className="text-gray-700">{report.organizer}</p>
          </div>
        )}
      </div>
    </div>
  );
}
