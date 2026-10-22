"use server";

import { prisma } from "@/lib/prisma";
import { checkServerAdminRole } from "@/lib/permissions";
import { revalidatePath } from "next/cache";

export async function updateReportStatus(id: string, status: string) {
  await checkServerAdminRole();

  try {
    await prisma.report.update({
      where: { id },
      data: { status },
    });

    revalidatePath("/admin/reports");
    revalidatePath("/reports");
    return { success: true };
  } catch (error: any) {
    return { success: false, error: error.message };
  }
}
