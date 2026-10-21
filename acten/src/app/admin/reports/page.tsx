import { Search, Eye, Check, X } from 'lucide-react';

export default function AdminReports() {
  const reports = [
    { id: 1, title: "Youth Retreat in Port Harcourt", diocese: "Port Harcourt", submitter: "Fr. Michael", date: "2 hrs ago", status: "Pending" },
    { id: 2, title: "Lenten Charity Drive - Lagos", diocese: "Lagos", submitter: "St. Agnes Parish", date: "Yesterday", status: "Pending" },
    { id: 3, title: "Annual Evangelization Summary", diocese: "Abuja", submitter: "Diocesan Exec", date: "Last week", status: "Approved" },
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-serif text-brand-charcoal">Report Submissions Review</h1>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              placeholder="Search reports..."
              className="w-full pl-9 pr-4 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:border-brand-green"
            />
          </div>
          <div className="flex gap-2 text-sm">
            <select className="border border-gray-300 rounded px-3 py-1.5 outline-none">
              <option>Status: Pending</option>
              <option>Status: Approved</option>
              <option>Status: All</option>
            </select>
          </div>
        </div>

        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white border-b text-sm text-gray-500">
              <th className="p-4 font-medium">Report Title</th>
              <th className="p-4 font-medium">Diocese</th>
              <th className="p-4 font-medium">Submitter</th>
              <th className="p-4 font-medium">Submitted</th>
              <th className="p-4 font-medium">Status</th>
              <th className="p-4 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((report) => (
              <tr key={report.id} className="border-b hover:bg-gray-50 transition-colors">
                <td className="p-4 font-medium text-gray-800">{report.title}</td>
                <td className="p-4 text-sm text-gray-600">{report.diocese}</td>
                <td className="p-4 text-sm text-gray-600">{report.submitter}</td>
                <td className="p-4 text-sm text-gray-600">{report.date}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    report.status === 'Pending' ? 'bg-amber-100 text-amber-800' : 'bg-green-100 text-green-800'
                  }`}>
                    {report.status}
                  </span>
                </td>
                <td className="p-4 text-right">
                  <div className="flex justify-end gap-2">
                    <button title="View Details" className="p-1.5 bg-gray-100 text-gray-600 hover:text-brand-green hover:bg-brand-light-grey rounded">
                      <Eye size={16} />
                    </button>
                    {report.status === 'Pending' && (
                      <>
                        <button title="Approve" className="p-1.5 bg-green-50 text-green-600 hover:bg-green-100 rounded">
                          <Check size={16} />
                        </button>
                        <button title="Reject" className="p-1.5 bg-red-50 text-red-600 hover:bg-red-100 rounded">
                          <X size={16} />
                        </button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
