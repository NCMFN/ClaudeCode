import Link from "next/link";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getServerSession(authOptions);

  if (!session || !session.user) {
    redirect("/api/auth/signin?callbackUrl=/admin");
  }

  const role = session.user.role;
  const isAdmin = role === "SUPER_ADMIN" || role === "EDITOR";

  if (!isAdmin) {
    return (
      <div className="flex flex-col min-h-screen bg-gray-50 items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-sm border border-gray-200 text-center">
          <h2 className="text-2xl font-bold text-red-600">Access Denied</h2>
          <p className="text-gray-600">You do not have permission to view the administration dashboard.</p>
          <Link href="/" className="inline-block px-4 py-2 bg-acten-green text-white rounded hover:bg-acten-green-700">
            Return to Homepage
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-acten-charcoal text-white flex-shrink-0 hidden md:flex flex-col">
        <div className="h-20 flex items-center px-6 bg-acten-green border-b border-acten-green-700">
          <Link href="/admin" className="font-serif text-xl font-bold text-acten-gold">
            ACTEN Admin
          </Link>
        </div>
        <div className="flex-grow py-6 px-4 space-y-1 overflow-y-auto">
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 mt-4 px-2">Dashboard</div>
          <Link href="/admin" className="block px-3 py-2 rounded-md hover:bg-gray-800 transition-colors">Overview</Link>

          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 mt-6 px-2">Content</div>
          <Link href="/admin/news" className="block px-3 py-2 rounded-md hover:bg-gray-800 transition-colors">News & Articles</Link>
          <Link href="/admin/events" className="block px-3 py-2 rounded-md hover:bg-gray-800 transition-colors">Events</Link>
          <Link href="/admin/resources" className="block px-3 py-2 rounded-md hover:bg-gray-800 transition-colors">Resources</Link>
          <Link href="/admin/gallery" className="block px-3 py-2 rounded-md hover:bg-gray-800 transition-colors">Gallery</Link>

          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 mt-6 px-2">Moderation</div>
          <Link href="/admin/reports" className="block px-3 py-2 rounded-md hover:bg-gray-800 transition-colors flex justify-between items-center">
            Diocesan Reports
            <span className="bg-acten-gold text-acten-charcoal text-xs font-bold px-2 py-0.5 rounded-full">New</span>
          </Link>
          <Link href="/admin/messages" className="block px-3 py-2 rounded-md hover:bg-gray-800 transition-colors">Contact Messages</Link>

          {role === "SUPER_ADMIN" && (
            <>
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 mt-6 px-2">System</div>
              <Link href="/admin/users" className="block px-3 py-2 rounded-md hover:bg-gray-800 transition-colors">Users & Roles</Link>
              <Link href="/admin/settings" className="block px-3 py-2 rounded-md hover:bg-gray-800 transition-colors">Settings</Link>
            </>
          )}
        </div>
        <div className="p-4 bg-gray-900 border-t border-gray-800">
          <div className="flex items-center">
            <div className="w-8 h-8 rounded-full bg-acten-gold flex items-center justify-center text-acten-charcoal font-bold text-sm">
              {session.user.name?.charAt(0) || 'A'}
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-white">{session.user.name}</p>
              <p className="text-xs text-gray-400">{session.user.role}</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 md:hidden">
          <Link href="/admin" className="font-serif text-lg font-bold text-acten-green">
            ACTEN Admin
          </Link>
          <button className="p-2 text-gray-500 hover:text-gray-900 focus:outline-none">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
