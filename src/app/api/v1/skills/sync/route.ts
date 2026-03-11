import { NextResponse } from 'next/server';
import { getDB, initDB } from '@/lib/db';
import { readFileSync, readdirSync, existsSync, statSync } from 'fs';
import { join } from 'path';

// Simple YAML frontmatter parser (no extra dependency needed)
function parseSkillFile(content: string, fallbackName: string) {
  let name = fallbackName;
  let description = "";
  
  if (content.startsWith("---")) {
    const parts = content.split("---");
    if (parts.length >= 3) {
      const frontmatter = parts[1];
      // Simple key: value parsing
      for (const line of frontmatter.split("\n")) {
        const match = line.match(/^(\w+)\s*:\s*(.+)$/);
        if (match) {
          if (match[1] === "name") name = match[2].trim();
          if (match[1] === "description") description = match[2].trim();
        }
      }
    }
  }
  
  return { name, description };
}

function findSkillsDir(): string | null {
  const candidates = [
    join(process.cwd(), "aiskills-repo", "skills"),
    join(process.cwd(), "api", "aiskills-repo", "skills"),
    join(process.cwd(), "..", "aiskills-repo", "skills"),
  ];
  
  for (const p of candidates) {
    if (existsSync(p)) return p;
  }
  return null;
}

export async function POST() {
  try {
    await initDB();
    const sql = getDB();
    
    const skillsDir = findSkillsDir();
    if (!skillsDir) {
      return NextResponse.json(
        { status: "error", detail: `Skills directory not found. CWD: ${process.cwd()}` },
        { status: 404 }
      );
    }
    
    const dirs = readdirSync(skillsDir);
    let count = 0;
    
    for (const dir of dirs) {
      const dirPath = join(skillsDir, dir);
      if (!statSync(dirPath).isDirectory()) continue;
      
      let skillFile = join(dirPath, "SKILL.md");
      if (!existsSync(skillFile)) {
        skillFile = join(dirPath, "skill.md");
        if (!existsSync(skillFile)) continue;
      }
      
      const content = readFileSync(skillFile, "utf-8");
      const { name, description } = parseSkillFile(content, dir);
      
      // Upsert
      await sql`
        INSERT INTO skills (name, description, content, last_sync)
        VALUES (${name}, ${description}, ${content}, NOW())
        ON CONFLICT (name) DO UPDATE SET
          description = ${description},
          content = ${content},
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
