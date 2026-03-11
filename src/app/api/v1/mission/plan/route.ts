import { NextRequest, NextResponse } from 'next/server';
import { getDB, initDB } from '@/lib/db';
import { planMission } from '@/lib/gemini';

export async function POST(request: NextRequest) {
  try {
    await initDB();
    const sql = getDB();
    
    // Support both query params and body
    const { searchParams } = new URL(request.url);
    let goal = searchParams.get('goal') || '';
    let agent = 'antigravity';
    
    // Try to read from body (MissionModal sends JSON)
    try {
      const body = await request.json();
      if (body.objective) goal = body.objective;
      if (body.agent) agent = body.agent;
    } catch { /* query param fallback */ }

    if (!goal) {
      return NextResponse.json({ error: 'Mission objective is required' }, { status: 400 });
    }

    // Create Mission
    const title = `Mission: ${goal.substring(0, 40)}${goal.length > 40 ? '...' : ''}`;
    const missionRes = await sql`
      INSERT INTO missions (title, description, status)
      VALUES (${title}, ${goal}, 'planned')
      RETURNING id, title, status
    `;
    const mission = missionRes[0];

    // Dynamic LLM Planning with Gemini
    let tasks: Array<{ label: string; skill: string; order: number }>;
    let planningMethod = 'gemini';

    try {
      tasks = await planMission(goal);
    } catch (llmError) {
      // Fallback to static tasks if Gemini is unavailable
      console.warn("Gemini unavailable, using fallback:", llmError);
      planningMethod = 'fallback';
      tasks = [
        { label: "Research & context analysis", skill: "docs-writer", order: 0 },
        { label: "Architecture & system design", skill: "api-designer", order: 1 },
        { label: "Core implementation", skill: "skill-creator", order: 2 },
        { label: "Testing & quality review", skill: "test-engineer", order: 3 },
        { label: "Deployment & monitoring", skill: "devops-pipeline", order: 4 },
      ];
    }

    // Persist tasks in DB
    for (const t of tasks) {
      await sql`
        INSERT INTO tasks (mission_id, label, skill, status, "order")
        VALUES (${mission.id}, ${t.label}, ${t.skill}, 'pending', ${t.order})
      `;
    }
    
    return NextResponse.json({
      mission_id: `m_${mission.id}`,
      status: mission.status,
      goal,
      agent,
      planning_method: planningMethod,
      tasks_count: tasks.length,
      tasks: tasks.map(t => ({ label: t.label, skill: t.skill }))
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    console.error("Mission plan error:", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
