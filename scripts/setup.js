#!/usr/bin/env node
// ═══════════════════════════════════════════════════════════════════════════════
// NEXUS HUB — One-Command Setup Script
// Usage: node scripts/setup.js
// ═══════════════════════════════════════════════════════════════════════════════

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const ROOT = path.resolve(__dirname, '..');

function run(cmd, opts = {}) {
  console.log(`  > ${cmd}`);
  execSync(cmd, { stdio: 'inherit', cwd: ROOT, ...opts });
}

function banner() {
  console.log(`
╔══════════════════════════════════════════════════╗
║         🛰️  NEXUS HUB — SETUP WIZARD            ║
║         Nümtéma AI Foundry • v2.0                ║
╚══════════════════════════════════════════════════╝
`);
}

async function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(resolve => rl.question(question, ans => { rl.close(); resolve(ans.trim()); }));
}

async function main() {
  banner();

  // ── Step 1: Check Node.js ──
  console.log("▸ Step 1/5 — Checking Node.js...");
  try {
    const v = execSync('node -v', { encoding: 'utf-8' }).trim();
    console.log(`  ✅ Node.js ${v}\n`);
  } catch {
    console.log("  ❌ Node.js not found. Install from https://nodejs.org\n");
    process.exit(1);
  }

  // ── Step 2: Install dependencies ──
  console.log("▸ Step 2/5 — Installing dependencies...");
  run('npm install');
  console.log("  ✅ Dependencies installed\n");

  // ── Step 3: Database URL ──
  console.log("▸ Step 3/5 — Database configuration...");
  const envPath = path.join(ROOT, '.env.local');
  
  if (fs.existsSync(envPath)) {
    const content = fs.readFileSync(envPath, 'utf-8');
    if (content.includes('DATABASE_URL=') && !content.includes('user:password')) {
      console.log("  ✅ .env.local already configured\n");
    } else {
      const dbUrl = await ask("  Enter your Neon DATABASE_URL: ");
      if (dbUrl) {
        fs.writeFileSync(envPath, `DATABASE_URL=${dbUrl}\n`);
        console.log("  ✅ .env.local created\n");
      }
    }
  } else {
    const dbUrl = await ask("  Enter your Neon DATABASE_URL (or press Enter to skip): ");
    if (dbUrl) {
      fs.writeFileSync(envPath, `DATABASE_URL=${dbUrl}\n`);
      console.log("  ✅ .env.local created\n");
    } else {
      console.log("  ⚠️  Skipped. Create .env.local later with DATABASE_URL=...\n");
    }
  }

  // ── Step 4: Install skills for detected agents ──
  console.log("▸ Step 4/5 — Installing skills for AI agents...");
  try {
    run('node scripts/install-skills.js');
  } catch {
    console.log("  ⚠️  Skill installer had issues (non-critical)\n");
  }

  // ── Step 5: Sync database ──
  console.log("▸ Step 5/5 — Ready to launch!");
  console.log(`
╔══════════════════════════════════════════════════╗
║  ✅  SETUP COMPLETE                              ║
║                                                  ║
║  To start locally:                               ║
║    npm run dev                                   ║
║                                                  ║
║  To deploy to Vercel:                            ║
║    npx vercel --prod                             ║
║                                                  ║
║  To sync skills to database:                     ║
║    Open http://localhost:3000/skills              ║
║    Click "Sync Repository"                       ║
║                                                  ║
║  🛰️  Nümtéma AI Foundry • Proprietary            ║
╚══════════════════════════════════════════════════╝
`);
}

main().catch(console.error);
