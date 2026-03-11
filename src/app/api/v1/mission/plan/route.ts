import { NextRequest, NextResponse } from 'next/server';
import { getDB, initDB } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    await initDB();
    const sql = getDB();
    
    const { searchParams } = new URL(request.url);
    const goal = searchParams.get('goal') || 'New Mission';
    
    const title = `Mission: ${goal.substring(0, 30)}...`;
    
    const result = await sql`
      INSERT INTO missions (title, description, status)
      VALUES (${title}, ${goal}, 'planned')
      RETURNING id, title, description, status, created_at
    `;
    
    const mission = result[0];
    
    return NextResponse.json({
      mission_id: `m_${mission.id}`,
      status: mission.status,
      goal: goal,
      tasks: [
        { id: "t1", action: "Research market", skill: "context-builder" },
        { id: "t2", action: "Generate styleguide", skill: "ui-style-generator" }
      ]
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    console.error("Mission plan error:", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
