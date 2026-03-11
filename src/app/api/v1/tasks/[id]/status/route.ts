import { NextRequest, NextResponse } from 'next/server';
import { getDB, initDB } from '@/lib/db';

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    await initDB();
    const sql = getDB();
    const { id } = await params;
    const body = await request.json();
    const { status } = body;

    if (!['pending', 'running', 'done', 'paused', 'blocked'].includes(status)) {
      return NextResponse.json({ error: 'Invalid status' }, { status: 400 });
    }

    await sql`UPDATE tasks SET status = ${status} WHERE id = ${parseInt(id)}`;

    return NextResponse.json({ id: parseInt(id), status, updated: true });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
