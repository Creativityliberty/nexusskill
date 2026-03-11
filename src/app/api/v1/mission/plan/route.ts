import { NextRequest, NextResponse } from 'next/server';
import { getDB, initDB } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    await initDB();
    const sql = getDB();
    
    const { searchParams } = new URL(request.url);
    const goal = searchParams.get('goal') || 'New Mission';
    
    // Create Mission
    const title = `Mission: ${goal.substring(0, 30)}${goal.length > 30 ? '...' : ''}`;
    const missionRes = await sql`
      INSERT INTO missions (title, description, status)
      VALUES (${title}, ${goal}, 'planned')
      RETURNING id, title, status
    `;
    const mission = missionRes[0];

    // Create real tasks in DB
    const taskPrototypes = [
      { label: "Research market context", skill: "context-builder" },
      { label: "Generate system architecture", skill: "orchestra-forge" },
      { label: "Execute implementation pass", skill: "skill-creator" },
      { label: "Final Quality Review", skill: "review-pr" }
    ];

    for (let i = 0; i < taskPrototypes.length; i++) {
      const t = taskPrototypes[i];
      await sql`
        INSERT INTO tasks (mission_id, label, skill, status, "order")
        VALUES (${mission.id}, ${t.label}, ${t.skill}, 'pending', ${i})
      `;
    }
    
    return NextResponse.json({
      mission_id: `m_${mission.id}`,
      status: mission.status,
      goal: goal,
      tasks_count: taskPrototypes.length
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    console.error("Mission plan error:", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
