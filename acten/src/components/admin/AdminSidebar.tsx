import Link from 'next/link';
import { LayoutDashboard, FileText, Calendar, FolderOpen, LogOut, FileCheck } from 'lucide-react';
import { signOut } from 'next-auth/react';

export default function AdminSidebar() {
  const links = [
    { href: "/admin", label: "Dashboard", icon: LayoutDashboard },
    { href: "/admin/articles", label: "Articles & News", icon: FileText },
    { href: "/admin/events", label: "Events", icon: Calendar },
    { href: "/admin/reports", label: "Reports Review", icon: FileCheck },
    { href: "/admin/resources", label: "Resources", icon: FolderOpen },
  ];

  return (
    <aside className="w-64 bg-brand-charcoal text-white min-h-screen flex flex-col fixed h-full z-10">
      <div className="p-6 border-b border-gray-700">
        <h2 className="text-xl font-serif text-brand-gold">ACTEN Admin</h2>
        <p className="text-xs text-gray-400 mt-1">Content Management</p>
      </div>

      <nav className="flex-1 py-6">
        <ul className="space-y-2 px-4">
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="flex items-center gap-3 px-4 py-3 rounded-md text-gray-300 hover:bg-gray-800 hover:text-brand-gold transition-colors"
                >
                  <Icon size={18} />
                  <span className="font-medium text-sm">{link.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="p-4 border-t border-gray-700">
        <button
          onClick={() => signOut({ callbackUrl: '/login' })}
          className="flex items-center gap-3 w-full px-4 py-3 text-sm font-medium text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors"
        >
          <LogOut size={18} />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
