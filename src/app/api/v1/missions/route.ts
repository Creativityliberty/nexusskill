import { NextResponse } from 'next/server';
import { getDB, initDB } from '@/lib/db';

export async function GET() {
  try {
    await initDB();
    const sql = getDB();
    const missions = await sql`SELECT * FROM missions ORDER BY created_at DESC`;
    return NextResponse.json(missions);
  } catch (error) {
    console.error("Missions GET error:", error);
    return NextResponse.json([]);
  }
}
