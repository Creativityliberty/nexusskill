import { NextResponse } from 'next/server';
import { getDB, initDB } from '@/lib/db';
import { SKILLS_CATALOG } from '@/lib/skills-data';

export async function POST() {
  try {
    await initDB();
    const sql = getDB();
    
    let count = 0;
    
    for (const skill of SKILLS_CATALOG) {
      await sql`
        INSERT INTO skills (name, description, content, last_sync)
        VALUES (${skill.name}, ${skill.description}, ${skill.description}, NOW())
        ON CONFLICT (name) DO UPDATE SET
          description = ${skill.description},
          content = ${skill.description},
          last_sync = NOW()
      `;
      count++;
    }
    
    return NextResponse.json({
      status: "success",
      message: `Orchestration complete: ${count} skills synchronized from Mesh.`
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    console.error("Sync error:", message);
    return NextResponse.json(
      { status: "error", detail: message },
      { status: 500 }
    );
  }
}
