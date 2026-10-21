import Link from 'next/link';
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";
import { redirect } from 'next/navigation';

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const session = await getServerSession(authOptions);

  if (!session || !session.user || ((session.user as any).role !== "SuperAdmin" && (session.user as any).role !== "Editor")) {
    redirect("/api/auth/signin?callbackUrl=/admin");
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-acten-charcoal text-white flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h2 className="text-xl font-serif font-bold text-acten-gold">ACTEN Admin</h2>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link href="/admin" className="block px-4 py-2 rounded hover:bg-gray-700">Dashboard</Link>
          <Link href="/admin/articles" className="block px-4 py-2 rounded hover:bg-gray-700">Articles</Link>
          <Link href="/admin/events" className="block px-4 py-2 rounded hover:bg-gray-700">Events</Link>
          <Link href="/admin/reports" className="block px-4 py-2 rounded hover:bg-gray-700">Reports</Link>
        </nav>
        <div className="p-4 border-t border-gray-700">
          <Link href="/" className="text-sm text-gray-400 hover:text-white">&larr; Back to Site</Link>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-gray-50">
        <header className="bg-white shadow-sm p-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-800">Dashboard</h1>
          <div className="text-sm text-gray-600">{session.user.name} ({ (session.user as any).role })</div>
        </header>
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
