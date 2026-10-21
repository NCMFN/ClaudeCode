import { prisma } from "@/lib/prisma";



export default async function AdminDashboardPage() {
  const articlesCount = await prisma.article.count();
  const pendingReportsCount = await prisma.report.count({ where: { status: 'Pending' } });
  const upcomingEventsCount = await prisma.event.count({ where: { status: 'Upcoming' } });

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Overview</h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-gray-500 text-sm font-medium">Total Articles</h3>
          <p className="text-3xl font-bold text-acten-green mt-2">{articlesCount}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-gray-500 text-sm font-medium">Pending Reports</h3>
          <p className="text-3xl font-bold text-acten-burgundy mt-2">{pendingReportsCount}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-gray-500 text-sm font-medium">Upcoming Events</h3>
          <p className="text-3xl font-bold text-acten-gold mt-2">{upcomingEventsCount}</p>
        </div>
      </div>
    </div>
  );
}
