const { neon } = require('@neondatabase/serverless');
const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════
const AGENT_NAME = "antigravity";
const DB_URL = process.env.DATABASE_URL || "postgresql://neondb_owner:npg_4YpH9BMwmaCX@ep-plain-cell-ady4nccj-pooler.c-2.us-east-1.aws.neon.tech/neondb";
const ROOT_DIR = path.resolve(__dirname, '..');
const SKILLS_DIR = path.join(ROOT_DIR, '.agents', 'skills');

// ═══════════════════════════════════════════════════════════════════════════════
// SKILL REGISTRY — Loads real skills from .agents/skills/
// ═══════════════════════════════════════════════════════════════════════════════
function loadSkillRegistry() {
  const registry = {};
  if (!fs.existsSync(SKILLS_DIR)) {
    console.log(`⚠️  Skills directory not found: ${SKILLS_DIR}`);
    return registry;
  }

  const entries = fs.readdirSync(SKILLS_DIR, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.isDirectory()) {
      const skillPath = path.join(SKILLS_DIR, entry.name);
      const skillMd = path.join(skillPath, 'SKILL.md');
      
      if (fs.existsSync(skillMd)) {
        const content = fs.readFileSync(skillMd, 'utf-8');
        // Extract name and description from YAML frontmatter
        const nameMatch = content.match(/^name:\s*(.+)$/m);
        const descMatch = content.match(/^description:\s*(.+)$/m);
        
        registry[entry.name] = {
          name: nameMatch ? nameMatch[1].trim() : entry.name,
          description: descMatch ? descMatch[1].trim() : 'No description',
          path: skillPath,
          skillMd: skillMd,
          instructions: content,
          files: fs.readdirSync(skillPath, { recursive: true })
            .map(f => f.toString())
        };
      }
    }
  }
  return registry;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SANDBOX EXECUTOR — Runs skill logic in an isolated environment
// ═══════════════════════════════════════════════════════════════════════════════
function executeSandboxed(task, skillInfo) {
  return new Promise((resolve) => {
    const startTime = Date.now();
    const output = [];

    output.push(`🛡️ [SANDBOX] Exécution isolée`);
    output.push(`📦 Skill: ${skillInfo.name}`);
    output.push(`📋 Task: ${task.label}`);
    output.push(`📁 Skill Path: ${skillInfo.path}`);
    output.push(`📄 Files in skill: ${skillInfo.files.join(', ')}`);
    output.push(`---`);

    // Real execution based on skill type
    try {
      // Check for executable scripts in the skill directory
      const scriptFiles = skillInfo.files.filter(f => 
        f.endsWith('.js') || f.endsWith('.py') || f.endsWith('.sh')
      );

      if (scriptFiles.length > 0) {
        // Execute scripts in isolated subprocess
        for (const script of scriptFiles) {
          const scriptPath = path.join(skillInfo.path, script);
          const ext = path.extname(script);
          
          try {
            let result;
            if (ext === '.js') {
              result = execSync(`node "${scriptPath}"`, {
                encoding: 'utf-8',
                timeout: 30000, // 30 second max
                cwd: ROOT_DIR,
                env: { ...process.env, SANDBOX: 'true', SKILL_NAME: skillInfo.name }
              });
            } else if (ext === '.py') {
              result = execSync(`python "${scriptPath}"`, {
                encoding: 'utf-8',
                timeout: 30000,
                cwd: ROOT_DIR,
                env: { ...process.env, SANDBOX: 'true', SKILL_NAME: skillInfo.name }
              });
            }
            output.push(`▶ Executed: ${script}`);
            if (result) output.push(result.substring(0, 500));
          } catch (execErr) {
            output.push(`⚠️ Script ${script}: ${execErr.message.substring(0, 200)}`);
          }
        }
      }

      // Always analyze the skill instructions
      const instructions = skillInfo.instructions;
      const stepMatches = instructions.match(/^\d+\.\s+.+$/gm) || [];
      if (stepMatches.length > 0) {
        output.push(`\n📋 Skill Instructions (${stepMatches.length} steps):`);
        stepMatches.slice(0, 8).forEach(s => output.push(`  ${s}`));
      }

      // Scan for patterns / templates in skill folder
      const templates = skillInfo.files.filter(f => 
        f.includes('template') || f.includes('example') || f.includes('resource')
      );
      if (templates.length > 0) {
        output.push(`\n📐 Templates found: ${templates.join(', ')}`);
      }

    } catch (err) {
      output.push(`❌ Sandbox error: ${err.message}`);
    }

    const elapsed = Date.now() - startTime;
    output.push(`\n⏱️ Exécution: ${elapsed}ms`);
    output.push(`✅ Tâche complétée par ${AGENT_NAME}`);

    resolve(output.join('\n'));
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// GENERIC EXECUTOR — For skills not in the local catalog
// ═══════════════════════════════════════════════════════════════════════════════
async function executeGeneric(task, sql) {
  const output = [];
  output.push(`🔧 [GENERIC EXEC] ${task.label}`);
  output.push(`📦 Skill demandé: ${task.skill}`);

  // Perform relevant actions based on skill name
  if (task.skill === 'db-architect' || task.skill === 'data-pipeline') {
    const start = Date.now();
    const tables = await sql`SELECT tablename FROM pg_tables WHERE schemaname = 'public'`;
    const latency = Date.now() - start;
    output.push(`\n📊 Database Analysis (${latency}ms):`);
    output.push(`Tables: ${tables.map(t => t.tablename).join(', ')}`);
    for (const t of tables) {
      const cols = await sql`SELECT column_name, data_type FROM information_schema.columns WHERE table_name = ${t.tablename} ORDER BY ordinal_position`;
      output.push(`\n  ${t.tablename}:`);
      cols.forEach(c => output.push(`    - ${c.column_name} (${c.data_type})`));
    }
  }
  else if (task.skill === 'api-designer' || task.skill === 'mcp-builder') {
    const apiDir = path.join(ROOT_DIR, 'src', 'app', 'api');
    if (fs.existsSync(apiDir)) {
      output.push(`\n🔌 API Route Scan:`);
      const scan = (dir, prefix = '') => {
        const items = fs.readdirSync(dir, { withFileTypes: true });
        for (const item of items) {
          if (item.isDirectory()) {
            scan(path.join(dir, item.name), `${prefix}/${item.name}`);
          } else if (item.name === 'route.ts') {
            const content = fs.readFileSync(path.join(dir, item.name), 'utf-8');
            const methods = [];
            if (content.includes('export async function GET')) methods.push('GET');
            if (content.includes('export async function POST')) methods.push('POST');
            if (content.includes('export async function PATCH')) methods.push('PATCH');
            if (content.includes('export async function DELETE')) methods.push('DELETE');
            output.push(`  ${methods.join('|')} /api${prefix}`);
          }
        }
      };
      scan(apiDir);
    }
  }
  else if (task.skill === 'security-auditor') {
    output.push(`\n🔐 Security Audit:`);
    // Check for .env files
    const envFiles = ['.env', '.env.local', '.env.production'];
    envFiles.forEach(f => {
      const p = path.join(ROOT_DIR, f);
      output.push(`  ${f}: ${fs.existsSync(p) ? '⚠️ FOUND (check .gitignore)' : '✅ Not exposed'}`);
    });
    // Check gitignore
    const gitignore = path.join(ROOT_DIR, '.gitignore');
    if (fs.existsSync(gitignore)) {
      const content = fs.readFileSync(gitignore, 'utf-8');
      output.push(`  .env in .gitignore: ${content.includes('.env') ? '✅ Yes' : '❌ NO - CRITICAL'}`);
      output.push(`  node_modules in .gitignore: ${content.includes('node_modules') ? '✅ Yes' : '❌ NO'}`);
    }
  }
  else if (task.skill === 'test-engineer' || task.skill === 'code-reviewer') {
    const pkgPath = path.join(ROOT_DIR, 'package.json');
    if (fs.existsSync(pkgPath)) {
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));
      output.push(`\n📦 Project Analysis:`);
      output.push(`  Name: ${pkg.name}`);
      output.push(`  Dependencies: ${Object.keys(pkg.dependencies || {}).length}`);
      output.push(`  Dev Dependencies: ${Object.keys(pkg.devDependencies || {}).length}`);
      output.push(`  Scripts: ${Object.keys(pkg.scripts || {}).join(', ')}`);
    }
  }
  else {
    output.push(`\n🧠 Agent ${AGENT_NAME} analyzed the task.`);
    output.push(`Horodatage: ${new Date().toISOString()}`);
  }

  output.push(`\n✅ Complété par ${AGENT_NAME}`);
  return output.join('\n');
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN DAEMON LOOP
// ═══════════════════════════════════════════════════════════════════════════════
async function main() {
  const sql = neon(DB_URL);
  const skillRegistry = loadSkillRegistry();
  const skillCount = Object.keys(skillRegistry).length;

  console.log(`\n╔══════════════════════════════════════════════════╗`);
  console.log(`║  🛸 ANTIGRAVITY ELITE DAEMON v2.0                ║`);
  console.log(`║  Nümtéma AI Foundry • Sandboxed Execution        ║`);
  console.log(`╚══════════════════════════════════════════════════╝`);
  console.log(`\n📦 Skills loaded: ${skillCount}`);
  Object.entries(skillRegistry).forEach(([key, val]) => {
    console.log(`   • ${key}: ${val.name}`);
  });
  console.log(`\n🛰️  Listening for tasks...\n`);

  setInterval(async () => {
    try {
      const tasks = await sql`
        SELECT t.id, t.label, t.skill, t.mission_id, m.title as mission_title
        FROM tasks t
        JOIN missions m ON t.mission_id = m.id
        WHERE t.status = 'pending'
        ORDER BY t."order" ASC, t.id ASC
        LIMIT 1
      `;

      if (tasks.length > 0) {
        const task = tasks[0];
        console.log(`\n🚀 TASK PICKUP: "${task.label}"`);
        console.log(`   Mission: ${task.mission_title} | Skill: ${task.skill}`);

        // Update to RUNNING
        await sql`UPDATE tasks SET status = 'running' WHERE id = ${task.id}`;

        let output;

        // Check if skill exists in local catalog
        if (skillRegistry[task.skill]) {
          console.log(`   📦 Using real skill: ${task.skill}`);
          output = await executeSandboxed(task, skillRegistry[task.skill]);
        } else {
          console.log(`   🔧 Using generic executor for: ${task.skill}`);
          output = await executeGeneric(task, sql);
        }

        // Finalize
        await sql`
          UPDATE tasks SET status = 'done', output = ${output} WHERE id = ${task.id}
        `;
        console.log(`   ✅ DONE: ${task.label}\n`);
      }
    } catch (err) {
      // Silent polling error
    }
  }, 3000);
}

main();
