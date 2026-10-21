import { prisma } from "@/lib/prisma";
import { updateReportStatus } from "./actions";



export default async function AdminReportsPage() {
  const reports = await prisma.report.findMany({
    orderBy: { createdAt: "desc" },
  });

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Review Reports</h2>
      </div>
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Diocese / Organizer</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date Submitted</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200 text-gray-900">
            {reports.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center text-gray-500">No reports submitted.</td>
              </tr>
            )}
            {reports.map((report) => (
              <tr key={report.id}>
                <td className="px-6 py-4 whitespace-nowrap">{report.title}</td>
                <td className="px-6 py-4 whitespace-nowrap">{report.diocese} / {report.organizer}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    report.status === 'Approved' ? 'bg-green-100 text-green-800' :
                    report.status === 'Rejected' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {report.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">{new Date(report.createdAt).toLocaleDateString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium flex justify-end space-x-2">
                  <form action={async () => {
                    "use server";
                    await updateReportStatus(report.id, "Approved");
                  }}>
                    <button className="text-acten-green hover:underline">Approve</button>
                  </form>
                  <form action={async () => {
                    "use server";
                    await updateReportStatus(report.id, "Rejected");
                  }}>
                    <button className="text-red-600 hover:underline">Reject</button>
                  </form>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
