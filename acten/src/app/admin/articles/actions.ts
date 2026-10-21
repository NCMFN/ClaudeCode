"use server";

import { prisma } from "@/lib/prisma";
import { checkServerAdminRole } from "@/lib/permissions";
import { revalidatePath } from "next/cache";
import { z } from "zod";

const articleSchema = z.object({
  title: z.string().min(1, "Title is required"),
  content: z.string().min(1, "Content is required"),
  summary: z.string().optional(),
  status: z.enum(["Draft", "Published", "Archived"]),
});

export async function createArticle(formData: FormData) {
  const user = await checkServerAdminRole();
  // @ts-expect-error custom user type
  const authorId = user.id;

  const result = articleSchema.safeParse({
    title: formData.get("title"),
    content: formData.get("content"),
    summary: formData.get("summary"),
    status: formData.get("status"),
  });

  if (!result.success) {
    return { success: false, error: result.error.issues[0].message };
  }

  const { title, content, summary, status } = result.data;
  const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)+/g, "");

  try {
    await prisma.article.create({
      data: {
        title,
        slug,
        content,
        summary: summary || null,
        status,
        authorId,
        publishedAt: status === "Published" ? new Date() : null,
      },
    });

    revalidatePath("/admin/articles");
    revalidatePath("/news");
    return { success: true };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
}

export async function updateArticle(id: string, formData: FormData) {
  await checkServerAdminRole();

  const result = articleSchema.safeParse({
    title: formData.get("title"),
    content: formData.get("content"),
    summary: formData.get("summary"),
    status: formData.get("status"),
  });

  if (!result.success) {
    return { success: false, error: result.error.issues[0].message };
  }

  const { title, content, summary, status } = result.data;

  try {
    const existing = await prisma.article.findUnique({ where: { id } });
    if (!existing) throw new Error("Article not found");

    await prisma.article.update({
      where: { id },
      data: {
        title,
        content,
        summary: summary || null,
        status,
        publishedAt: status === "Published" && !existing.publishedAt ? new Date() : existing.publishedAt,
      },
    });

    revalidatePath("/admin/articles");
    revalidatePath("/news");
    return { success: true };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
}

export async function deleteArticle(id: string) {
  await checkServerAdminRole();

  try {
    await prisma.article.delete({ where: { id } });
    revalidatePath("/admin/articles");
    revalidatePath("/news");
    return { success: true };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
}
