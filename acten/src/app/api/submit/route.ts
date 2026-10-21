import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function POST(req: Request) {
  try {
    const data = await req.json();

    // Basic validation
    if (!data.submitterName || !data.contactEmail || !data.title || !data.activityDate || !data.summary || !data.content) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    const report = await prisma.report.create({
      data: {
        submitterName: data.submitterName,
        contactEmail: data.contactEmail,
        diocese: data.diocese || null,
        parish: data.parish || null,
        title: data.title,
        activityDate: new Date(data.activityDate),
        location: data.location || null,
        summary: data.summary,
        content: data.content,
        status: 'PENDING',
      }
    });

    return NextResponse.json({ success: true, reportId: report.id }, { status: 201 });
  } catch (error) {
    console.error("Submission error:", error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
