"use server";

import { prisma } from "@/lib/prisma";
import { revalidatePath } from "next/cache";
import { z } from "zod";

const contactSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email address"),
  subject: z.string().min(1, "Subject is required"),
  message: z.string().min(1, "Message is required"),
});

export async function submitContact(formData: FormData) {
  const result = contactSchema.safeParse({
    name: formData.get("name"),
    email: formData.get("email"),
    subject: formData.get("subject"),
    message: formData.get("message"),
  });

  if (!result.success) {
    return { success: false, error: result.error.issues[0].message };
  }

  await prisma.contactSubmission.create({
    data: result.data,
  });

  return { success: true };
}

const reportSchema = z.object({
  title: z.string().min(1, "Title is required"),
  content: z.string().min(1, "Content is required"),
  venue: z.string().optional(),
  organizer: z.string().optional(),
  diocese: z.string().optional(),
});

export async function submitReport(formData: FormData) {
  const result = reportSchema.safeParse({
    title: formData.get("title"),
    content: formData.get("content"),
    venue: formData.get("venue"),
    organizer: formData.get("organizer"),
    diocese: formData.get("diocese"),
  });

  if (!result.success) {
    return { success: false, error: result.error.issues[0].message };
  }

  await prisma.report.create({
    data: {
      ...result.data,
      date: new Date(),
      status: "Pending",
    },
  });

  return { success: true };
}
