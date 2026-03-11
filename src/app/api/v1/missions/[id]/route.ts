import { NextRequest, NextResponse } from 'next/server';
import { getDB, initDB } from '@/lib/db';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    await initDB();
    const sql = getDB();
    const { id } = await params;

    const mission = await sql`SELECT * FROM missions WHERE id = ${parseInt(id)}`;
    if (mission.length === 0) {
      return NextResponse.json({ error: 'Mission not found' }, { status: 404 });
    }

    const tasks = await sql`
      SELECT * FROM tasks WHERE mission_id = ${parseInt(id)} ORDER BY "order"
    `;

    return NextResponse.json({
      ...mission[0],
      tasks
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
