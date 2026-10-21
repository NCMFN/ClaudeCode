"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createArticle } from "../actions";
import Link from "next/link";

export default function NewArticlePage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const result = await createArticle(formData);
    if (result.success) {
      router.push("/admin/articles");
    } else {
      setError(result.error || "Failed to create article");
    }
  }

  return (
    <div className="max-w-3xl mx-auto bg-white p-8 rounded-lg shadow-sm border border-gray-200">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Create New Article</h2>
        <Link href="/admin/articles" className="text-gray-500 hover:underline">Cancel</Link>
      </div>

      {error && <div className="mb-4 text-red-600 bg-red-50 p-3 rounded">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
          <input name="title" type="text" required className="w-full border border-gray-300 rounded-md px-4 py-2" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Summary</label>
          <textarea name="summary" rows={3} className="w-full border border-gray-300 rounded-md px-4 py-2"></textarea>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
          <textarea name="content" rows={10} required className="w-full border border-gray-300 rounded-md px-4 py-2"></textarea>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select name="status" className="w-full border border-gray-300 rounded-md px-4 py-2">
            <option value="Draft">Draft</option>
            <option value="Published">Published</option>
          </select>
        </div>

        <button type="submit" className="bg-acten-green text-white px-6 py-2 rounded-md font-bold hover:bg-opacity-90">
          Save Article
        </button>
      </form>
    </div>
  );
}
