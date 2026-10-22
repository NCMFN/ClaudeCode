"use client";
import AdminSidebar from "@/components/admin/AdminSidebar";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  if (status === "loading") {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!session) return null;

  return (
    <div className="flex min-h-screen bg-gray-50">
      <AdminSidebar />
      <div className="flex-1 ml-64 overflow-auto">
        {/* Admin Header */}
        <header className="bg-white border-b border-gray-200 px-8 py-4 flex justify-between items-center sticky top-0 z-10">
          <h2 className="text-xl font-medium text-gray-800">Dashboard</h2>
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium bg-brand-light-grey px-3 py-1 rounded text-brand-green">
              {session.user?.email}
            </span>
            <span className="text-sm text-gray-600">
              {session.user?.email}
            </span>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
