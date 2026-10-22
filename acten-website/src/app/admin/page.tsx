import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import prisma from "@/lib/prisma";
import Link from "next/link";

export default async function AdminDashboard() {
  const session = await getServerSession(authOptions);

  const [
    articleCount,
    eventCount,
    pendingReports,
    newMessages
  ] = await Promise.all([
    prisma.article.count(),
    prisma.event.count(),
    prisma.report.count({ where: { status: 'PENDING' } }),
    prisma.contactSubmission.count({ where: { status: 'NEW' } })
  ]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>
        <div className="text-sm text-gray-500">
          Welcome back, {session?.user?.name || 'Admin'}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-1">Total Articles</p>
              <h3 className="text-3xl font-bold text-gray-900">{articleCount}</h3>
            </div>
            <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center text-blue-600">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path></svg>
            </div>
          </div>
          <div className="mt-4">
            <Link href="/admin/news" className="text-sm text-blue-600 hover:underline font-medium">Manage articles &rarr;</Link>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-1">Total Events</p>
              <h3 className="text-3xl font-bold text-gray-900">{eventCount}</h3>
            </div>
            <div className="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center text-purple-600">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
            </div>
          </div>
          <div className="mt-4">
            <Link href="/admin/events" className="text-sm text-purple-600 hover:underline font-medium">Manage events &rarr;</Link>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 relative overflow-hidden">
          <div className="flex items-center justify-between relative z-10">
            <div>
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-1">Pending Reports</p>
              <h3 className="text-3xl font-bold text-gray-900">{pendingReports}</h3>
            </div>
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${pendingReports > 0 ? 'bg-amber-100 text-amber-600' : 'bg-gray-100 text-gray-400'}`}>
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            </div>
          </div>
          <div className="mt-4 relative z-10">
            <Link href="/admin/reports" className={`text-sm font-medium hover:underline ${pendingReports > 0 ? 'text-amber-600' : 'text-gray-500'}`}>Review reports &rarr;</Link>
          </div>
          {pendingReports > 0 && (
            <div className="absolute top-0 right-0 w-2 h-full bg-amber-400"></div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 relative overflow-hidden">
          <div className="flex items-center justify-between relative z-10">
            <div>
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-1">New Messages</p>
              <h3 className="text-3xl font-bold text-gray-900">{newMessages}</h3>
            </div>
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${newMessages > 0 ? 'bg-acten-green/10 text-acten-green' : 'bg-gray-100 text-gray-400'}`}>
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
            </div>
          </div>
          <div className="mt-4 relative z-10">
            <Link href="/admin/messages" className={`text-sm font-medium hover:underline ${newMessages > 0 ? 'text-acten-green' : 'text-gray-500'}`}>View messages &rarr;</Link>
          </div>
          {newMessages > 0 && (
            <div className="absolute top-0 right-0 w-2 h-full bg-acten-green"></div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link href="/admin/news/create" className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
              <div className="w-10 h-10 rounded bg-blue-50 text-blue-600 flex items-center justify-center mr-4">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
              </div>
              <div>
                <p className="font-medium text-gray-900">Publish New Article</p>
                <p className="text-sm text-gray-500">Create a news post or announcement</p>
              </div>
            </Link>

            <Link href="/admin/events/create" className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
              <div className="w-10 h-10 rounded bg-purple-50 text-purple-600 flex items-center justify-center mr-4">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
              </div>
              <div>
                <p className="font-medium text-gray-900">Add Upcoming Event</p>
                <p className="text-sm text-gray-500">Schedule a new gathering or mission</p>
              </div>
            </Link>

            <Link href="/admin/gallery/create" className="flex items-center p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
              <div className="w-10 h-10 rounded bg-pink-50 text-pink-600 flex items-center justify-center mr-4">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
              </div>
              <div>
                <p className="font-medium text-gray-900">Upload Photos</p>
                <p className="text-sm text-gray-500">Create a new gallery album</p>
              </div>
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">System Information</h2>
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <dl className="space-y-4 text-sm">
              <div className="flex justify-between border-b border-gray-200 pb-2">
                <dt className="text-gray-500">Environment</dt>
                <dd className="font-medium text-gray-900">{process.env.NODE_ENV}</dd>
              </div>
              <div className="flex justify-between border-b border-gray-200 pb-2">
                <dt className="text-gray-500">Database Connection</dt>
                <dd className="font-medium text-green-600 flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-green-500"></span> Active
                </dd>
              </div>
              <div className="flex justify-between border-b border-gray-200 pb-2">
                <dt className="text-gray-500">Next.js Version</dt>
                <dd className="font-medium text-gray-900">14.2.4</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Timezone</dt>
                <dd className="font-medium text-gray-900">UTC / WAT</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}
