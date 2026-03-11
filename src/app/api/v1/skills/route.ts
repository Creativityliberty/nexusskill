import { NextResponse } from 'next/server';
import { getDB, initDB } from '@/lib/db';

export async function GET() {
  try {
    await initDB();
    const sql = getDB();
    const skills = await sql`SELECT id, name, description, last_sync FROM skills ORDER BY name`;
    
    if (skills.length === 0) {
      return NextResponse.json([
        { name: "skill-creator", description: "Guide for creating effective Claude Code skills." },
        { name: "ui-style-generator", description: "Generate a complete UI Design System." }
      ]);
    }
    
    return NextResponse.json(skills);
  } catch (error) {
    console.error("Skills GET error:", error);
    return NextResponse.json(
      [{ name: "skill-creator", description: "Guide for creating effective Claude Code skills." },
       { name: "ui-style-generator", description: "Generate a complete UI Design System." }]
    );
  }
}
