import { Plus, Search, Edit, Trash2 } from "lucide-react";

export default function AdminArticles() {
  const articles = [
    { id: 1, title: "Lenten Outreach Touches Hundreds", status: "Published", date: "Mar 15, 2026", author: "Admin" },
    { id: 2, title: "National Evangelizers Conference", status: "Published", date: "Feb 28, 2026", author: "Editor" },
    { id: 3, title: "Guidelines for Digital Missionaries", status: "Draft", date: "Mar 10, 2026", author: "Admin" },
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-serif text-brand-charcoal">Articles & News</h1>
        <button className="bg-brand-green text-white px-4 py-2 rounded font-medium flex items-center gap-2 hover:bg-opacity-90">
          <Plus size={18} /> New Article
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              placeholder="Search articles..."
              className="w-full pl-9 pr-4 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:border-brand-green"
            />
          </div>
          <div className="flex gap-2 text-sm">
            <select className="border border-gray-300 rounded px-3 py-1.5 outline-none">
              <option>All Statuses</option>
              <option>Published</option>
              <option>Draft</option>
            </select>
          </div>
        </div>

        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white border-b text-sm text-gray-500">
              <th className="p-4 font-medium">Title</th>
              <th className="p-4 font-medium">Status</th>
              <th className="p-4 font-medium">Author</th>
              <th className="p-4 font-medium">Date</th>
              <th className="p-4 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {articles.map((article) => (
              <tr key={article.id} className="border-b hover:bg-gray-50 transition-colors">
                <td className="p-4">
                  <p className="font-medium text-gray-800">{article.title}</p>
                </td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    article.status === 'Published' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {article.status}
                  </span>
                </td>
                <td className="p-4 text-sm text-gray-600">{article.author}</td>
                <td className="p-4 text-sm text-gray-600">{article.date}</td>
                <td className="p-4 text-right">
                  <div className="flex justify-end gap-3 text-gray-400">
                    <button className="hover:text-brand-green"><Edit size={16} /></button>
                    <button className="hover:text-red-500"><Trash2 size={16} /></button>
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
