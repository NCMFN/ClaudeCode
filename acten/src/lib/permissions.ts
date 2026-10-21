import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";

export async function checkServerAdminRole() {
  const session = await getServerSession(authOptions);

  if (!session || !session.user || (session.user as any).role !== "SuperAdmin" && (session.user as any).role !== "Editor") {
    throw new Error("Unauthorized. Required role: SuperAdmin or Editor.");
  }

  return session.user;
}

export async function getSessionUser() {
  const session = await getServerSession(authOptions);
  return session?.user;
}
