import { Users, FileText, CheckCircle, Calendar } from 'lucide-react';

export default function AdminDashboard() {
  const stats = [
    { label: "Published Articles", count: 24, icon: FileText, color: "text-blue-600" },
    { label: "Pending Reports", count: 5, icon: CheckCircle, color: "text-amber-600" },
    { label: "Upcoming Events", count: 3, icon: Calendar, color: "text-green-600" },
    { label: "Registered Users", count: 12, icon: Users, color: "text-purple-600" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-serif text-brand-charcoal mb-8">Overview</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 mb-1">{stat.label}</p>
                <h3 className="text-3xl font-bold text-gray-800">{stat.count}</h3>
              </div>
              <div className={`p-3 bg-gray-50 rounded-full ${stat.color}`}>
                <Icon size={24} />
              </div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-lg font-medium text-gray-800 mb-4 border-b pb-2">Recent Submissions (Pending Review)</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 hover:bg-gray-50 rounded cursor-pointer">
              <div>
                <p className="font-medium text-gray-800 text-sm">Youth Retreat in Port Harcourt</p>
                <p className="text-xs text-gray-500 mt-1">Submitted 2 hours ago by Fr. Michael</p>
              </div>
              <span className="px-2 py-1 bg-amber-100 text-amber-800 text-xs rounded">Review</span>
            </div>
            <div className="flex justify-between items-center p-3 hover:bg-gray-50 rounded cursor-pointer">
              <div>
                <p className="font-medium text-gray-800 text-sm">Lenten Charity Drive - Lagos</p>
                <p className="text-xs text-gray-500 mt-1">Submitted yesterday by St. Agnes Parish</p>
              </div>
              <span className="px-2 py-1 bg-amber-100 text-amber-800 text-xs rounded">Review</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-lg font-medium text-gray-800 mb-4 border-b pb-2">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            <button className="p-4 border border-gray-200 rounded flex flex-col items-center justify-center gap-2 hover:bg-brand-green hover:text-white transition-colors group">
              <FileText size={24} className="text-gray-400 group-hover:text-white" />
              <span className="text-sm font-medium">New Article</span>
            </button>
            <button className="p-4 border border-gray-200 rounded flex flex-col items-center justify-center gap-2 hover:bg-brand-green hover:text-white transition-colors group">
              <Calendar size={24} className="text-gray-400 group-hover:text-white" />
              <span className="text-sm font-medium">Add Event</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
