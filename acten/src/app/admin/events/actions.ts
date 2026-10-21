"use server";

import { prisma } from "@/lib/prisma";
import { checkServerAdminRole } from "@/lib/permissions";
import { revalidatePath } from "next/cache";
import { z } from "zod";

const eventSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().min(1, "Description is required"),
  startDate: z.string().min(1, "Start Date is required"),
  endDate: z.string().min(1, "End Date is required"),
  venue: z.string().optional(),
  isOnline: z.boolean(),
  status: z.enum(["Upcoming", "Ongoing", "Completed", "Cancelled"]),
});

export async function createEvent(formData: FormData) {
  await checkServerAdminRole();

  const result = eventSchema.safeParse({
    title: formData.get("title"),
    description: formData.get("description"),
    startDate: formData.get("startDate"),
    endDate: formData.get("endDate"),
    venue: formData.get("venue"),
    isOnline: formData.get("isOnline") === "true",
    status: formData.get("status"),
  });

  if (!result.success) {
    return { success: false, error: result.error.issues[0].message };
  }

  const { title, description, startDate, endDate, venue, isOnline, status } = result.data;
  const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)+/g, "");

  try {
    await prisma.event.create({
      data: {
        title,
        slug,
        description,
        startDate: new Date(startDate),
        endDate: new Date(endDate),
        venue: venue || null,
        isOnline,
        status,
      },
    });

    revalidatePath("/admin/events");
    revalidatePath("/events");
    return { success: true };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
}

export async function updateEvent(id: string, formData: FormData) {
  await checkServerAdminRole();

  const result = eventSchema.safeParse({
    title: formData.get("title"),
    description: formData.get("description"),
    startDate: formData.get("startDate"),
    endDate: formData.get("endDate"),
    venue: formData.get("venue"),
    isOnline: formData.get("isOnline") === "true",
    status: formData.get("status"),
  });

  if (!result.success) {
    return { success: false, error: result.error.issues[0].message };
  }

  const { title, description, startDate, endDate, venue, isOnline, status } = result.data;

  try {
    await prisma.event.update({
      where: { id },
      data: {
        title,
        description,
        startDate: new Date(startDate),
        endDate: new Date(endDate),
        venue: venue || null,
        isOnline,
        status,
      },
    });

    revalidatePath("/admin/events");
    revalidatePath("/events");
    return { success: true };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
}

export async function deleteEvent(id: string) {
  await checkServerAdminRole();

  try {
    await prisma.event.delete({ where: { id } });
    revalidatePath("/admin/events");
    revalidatePath("/events");
    return { success: true };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
}
