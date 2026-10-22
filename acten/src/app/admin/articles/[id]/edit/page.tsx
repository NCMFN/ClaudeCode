import { prisma } from "@/lib/prisma";
import { updateArticle } from "../../actions";
import Link from "next/link";
import { redirect } from "next/navigation";

export default async function EditArticlePage({ params }: { params: { id: string } }) {
  const article = await prisma.article.findUnique({ where: { id: params.id } });

  if (!article) {
    return <div>Article not found</div>;
  }

  async function handleSubmit(formData: FormData) {
    "use server";
    const result = await updateArticle(params.id, formData);
    if (result.success) {
      redirect("/admin/articles");
    }
  }

  return (
    <div className="max-w-3xl mx-auto bg-white p-8 rounded-lg shadow-sm border border-gray-200">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Edit Article</h2>
        <Link href="/admin/articles" className="text-gray-500 hover:underline">Cancel</Link>
      </div>

      <form action={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
          <input name="title" type="text" defaultValue={article.title} required className="w-full border border-gray-300 rounded-md px-4 py-2" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Summary</label>
          <textarea name="summary" rows={3} defaultValue={article.summary || ""} className="w-full border border-gray-300 rounded-md px-4 py-2"></textarea>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
          <textarea name="content" rows={10} defaultValue={article.content} required className="w-full border border-gray-300 rounded-md px-4 py-2"></textarea>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select name="status" defaultValue={article.status} className="w-full border border-gray-300 rounded-md px-4 py-2">
            <option value="Draft">Draft</option>
            <option value="Published">Published</option>
            <option value="Archived">Archived</option>
          </select>
        </div>

        <button type="submit" className="bg-acten-green text-white px-6 py-2 rounded-md font-bold hover:bg-opacity-90">
          Update Article
        </button>
      </form>
    </div>
  );
}
