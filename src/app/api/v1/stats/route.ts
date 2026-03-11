import { NextResponse } from 'next/server';
import { getDB, initDB } from '@/lib/db';

export async function GET() {
  try {
    await initDB();
    const sql = getDB();

    const skillCount = await sql`SELECT COUNT(*) as count FROM skills`;
    const missionCount = await sql`SELECT COUNT(*) as count FROM missions`;
    const keyCount = await sql`SELECT COUNT(*) as count FROM api_keys`;

    const recentMissions = await sql`
      SELECT id, title, status, created_at 
      FROM missions 
      ORDER BY created_at DESC 
      LIMIT 5
    `;

    return NextResponse.json({
      skills: Number(skillCount[0]?.count || 0),
      missions: Number(missionCount[0]?.count || 0),
      keys: Number(keyCount[0]?.count || 0),
      recent_missions: recentMissions,
      status: "operational"
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    return NextResponse.json({
      skills: 0,
      missions: 0,
      keys: 0,
      recent_missions: [],
      status: "degraded",
      error: message
    });
  }
}
