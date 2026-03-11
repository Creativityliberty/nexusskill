#!/usr/bin/env node
// ═══════════════════════════════════════════════════════════════════════════════
// NEXUS SKILL INSTALLER — Universal AI Agent Skill Installer
// Supports 39 AI coding agents. Detects installed agents and
// creates symlinks from each agent's skills directory to .agents/skills/
// ═══════════════════════════════════════════════════════════════════════════════

const fs = require('fs');
const path = require('path');
const os = require('os');

const HOME = os.homedir();

// ───────── Agent Registry ─────────
const AGENTS = [
  // Universal agents (read directly from .agents/skills/)
  { name: "Amp",             dir: ".agents/skills/", detect: path.join(HOME, ".config/amp"),         type: "universal" },
  { name: "Codex",           dir: ".agents/skills/", detect: path.join(HOME, ".codex"),              type: "universal" },
  { name: "Gemini CLI",      dir: ".agents/skills/", detect: path.join(HOME, ".config/gemini"),      type: "universal" },
  { name: "GitHub Copilot",  dir: ".agents/skills/", detect: path.join(HOME, ".config/github-copilot"), type: "universal" },
  { name: "Kimi Code CLI",   dir: ".agents/skills/", detect: path.join(HOME, ".kimi"),               type: "universal" },
  { name: "OpenCode",        dir: ".agents/skills/", detect: path.join(HOME, ".config/opencode"),    type: "universal" },

  // Project-scoped agents (need symlinks)
  { name: "AdaL",            dir: ".adal/skills/",       detect: path.join(HOME, ".adal")               },
  { name: "Antigravity",     dir: ".agent/skills/",      detect: path.join(HOME, ".agent")              },
  { name: "Augment",         dir: ".augment/skills/",    detect: path.join(HOME, ".augment")            },
  { name: "Claude Code",     dir: ".claude/skills/",     detect: path.join(HOME, ".claude")             },
  { name: "Cline",           dir: ".cline/skills/",      detect: path.join(HOME, ".cline")              },
  { name: "CodeBuddy",       dir: ".codebuddy/skills/",  detect: path.join(HOME, ".codebuddy")          },
  { name: "Command Code",    dir: ".commandcode/skills/", detect: path.join(HOME, ".commandcode")       },
  { name: "Continue",        dir: ".continue/skills/",   detect: path.join(HOME, ".continue")           },
  { name: "Crush",           dir: ".crush/skills/",      detect: path.join(HOME, ".config/crush")       },
  { name: "Cursor",          dir: ".cursor/skills/",     detect: path.join(HOME, ".cursor")             },
  { name: "Droid",           dir: ".factory/skills/",    detect: path.join(HOME, ".factory")            },
  { name: "Goose",           dir: ".goose/skills/",      detect: path.join(HOME, ".config/goose")       },
  { name: "iFlow CLI",       dir: ".iflow/skills/",      detect: path.join(HOME, ".iflow")              },
  { name: "Junie",           dir: ".junie/skills/",      detect: path.join(HOME, ".junie")              },
  { name: "Kilo Code",       dir: ".kilocode/skills/",   detect: path.join(HOME, ".kilocode")           },
  { name: "Kiro CLI",        dir: ".kiro/skills/",       detect: path.join(HOME, ".kiro")               },
  { name: "Kode",            dir: ".kode/skills/",       detect: path.join(HOME, ".kode")               },
  { name: "MCPJam",          dir: ".mcpjam/skills/",     detect: path.join(HOME, ".mcpjam")             },
  { name: "Mistral Vibe",    dir: ".vibe/skills/",       detect: path.join(HOME, ".vibe")               },
  { name: "Mux",             dir: ".mux/skills/",        detect: path.join(HOME, ".mux")                },
  { name: "Neovate",         dir: ".neovate/skills/",    detect: path.join(HOME, ".neovate")            },
  { name: "OpenClaw",        dir: "skills/",             detect: path.join(HOME, ".openclaw")           },
  { name: "OpenHands",       dir: ".openhands/skills/",  detect: path.join(HOME, ".openhands")          },
  { name: "Pi",              dir: ".pi/skills/",         detect: path.join(HOME, ".pi")                 },
  { name: "Pochi",           dir: ".pochi/skills/",      detect: path.join(HOME, ".pochi")              },
  { name: "Qoder",           dir: ".qoder/skills/",      detect: path.join(HOME, ".qoder")              },
  { name: "Qwen Code",       dir: ".qwen/skills/",       detect: path.join(HOME, ".qwen")               },
  { name: "Roo Code",        dir: ".roo/skills/",        detect: path.join(HOME, ".roo")                },
  { name: "Trae",            dir: ".trae/skills/",       detect: path.join(HOME, ".trae")               },
  { name: "Windsurf",        dir: ".windsurf/skills/",   detect: path.join(HOME, ".codeium/windsurf")   },
  { name: "Zencoder",        dir: ".zencoder/skills/",   detect: path.join(HOME, ".zencoder")           },
];

// ───────── Detection ─────────
function detectAgents() {
  const found = [];
  for (const agent of AGENTS) {
    try {
      if (fs.existsSync(agent.detect)) {
        found.push(agent);
      }
    } catch { /* skip */ }
  }
  return found;
}

// ───────── Symlink ─────────
function installSkills(projectRoot) {
  const sourceDir = path.join(projectRoot, ".agents", "skills");

  if (!fs.existsSync(sourceDir)) {
    console.log(`⚠  Source directory not found: ${sourceDir}`);
    console.log(`   Make sure .agents/skills/ exists with your skills.`);
    return;
  }

  const detected = detectAgents();
  console.log(`\n🛰️  NEXUS SKILL INSTALLER`);
  console.log(`   Source: ${sourceDir}`);
  console.log(`   Detected ${detected.length} agents on this machine.\n`);

  let installed = 0;
  let skipped = 0;

  for (const agent of detected) {
    if (agent.type === "universal") {
      console.log(`  ✅ ${agent.name.padEnd(18)} (universal — reads .agents/skills/ directly)`);
      installed++;
      continue;
    }

    const targetDir = path.join(projectRoot, agent.dir);
    const targetParent = path.dirname(targetDir);

    try {
      // Create parent directory if needed
      fs.mkdirSync(targetParent, { recursive: true });

      // Check if symlink already exists
      if (fs.existsSync(targetDir)) {
        const stats = fs.lstatSync(targetDir);
        if (stats.isSymbolicLink()) {
          console.log(`  ⏭  ${agent.name.padEnd(18)} (already linked)`);
          skipped++;
          continue;
        }
        // If it's a real directory, skip (don't destroy user data)
        if (stats.isDirectory()) {
          console.log(`  ⏭  ${agent.name.padEnd(18)} (dir exists — manual link needed)`);
          skipped++;
          continue;
        }
      }

      // Create symlink
      const symlinkType = process.platform === 'win32' ? 'junction' : 'dir';
      fs.symlinkSync(sourceDir, targetDir, symlinkType);
      console.log(`  🔗 ${agent.name.padEnd(18)} → ${agent.dir}`);
      installed++;
    } catch (err) {
      console.log(`  ❌ ${agent.name.padEnd(18)} — ${err.message}`);
    }
  }

  console.log(`\n   ─────────────────────────────────`);
  console.log(`   ✅ ${installed} installed  ⏭ ${skipped} skipped  📦 Total: ${detected.length}\n`);
}

// ───────── Main ─────────
const projectRoot = process.argv[2] || process.cwd();
installSkills(projectRoot);
