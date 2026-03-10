# Supported AI Agents — Complete Reference

Full mapping of all 39 AI coding agents supported by the skill installer.

## Universal Agents

These agents read directly from `.agents/skills/` — no symlinks needed.

| Agent | Skills Directory | Detection Path |
|-------|-----------------|----------------|
| Amp | `.agents/skills/` | `~/.config/amp/` |
| Codex | `.agents/skills/` | `~/.codex/` or `/etc/codex` |
| Gemini CLI | `.agents/skills/` | `~/.config/gemini/` |
| GitHub Copilot | `.agents/skills/` | `~/.config/github-copilot/` |
| Kimi Code CLI | `.agents/skills/` | `~/.kimi/` |
| OpenCode | `.agents/skills/` | `~/.config/opencode/` |

## Project-Scoped Agents

These agents have their own skills directory. The installer creates symlinks from
their directory back to `.agents/skills/`.

| Agent | Skills Directory | Detection Path |
|-------|-----------------|----------------|
| AdaL | `.adal/skills/` | `~/.adal/` |
| Antigravity | `.agent/skills/` | `~/.agent/` |
| Augment | `.augment/skills/` | `~/.augment/` |
| Claude Code | `.claude/skills/` | `~/.claude/` |
| Cline | `.cline/skills/` | `~/.cline/` |
| CodeBuddy | `.codebuddy/skills/` | `~/.codebuddy/` |
| Command Code | `.commandcode/skills/` | `~/.commandcode/` |
| Continue | `.continue/skills/` | `~/.continue/` |
| Crush | `.crush/skills/` | `~/.config/crush/` |
| Cursor | `.cursor/skills/` | `~/.cursor/` |
| Droid | `.factory/skills/` | `~/.factory/` |
| Goose | `.goose/skills/` | `~/.config/goose/` |
| iFlow CLI | `.iflow/skills/` | `~/.iflow/` |
| Junie | `.junie/skills/` | `~/.junie/` |
| Kilo Code | `.kilocode/skills/` | `~/.kilocode/` |
| Kiro CLI | `.kiro/skills/` | `~/.kiro/` |
| Kode | `.kode/skills/` | `~/.kode/` |
| MCPJam | `.mcpjam/skills/` | `~/.mcpjam/` |
| Mistral Vibe | `.vibe/skills/` | `~/.vibe/` |
| Mux | `.mux/skills/` | `~/.mux/` |
| Neovate | `.neovate/skills/` | `~/.neovate/` |
| OpenClaw | `skills/` | `~/.openclaw/` |
| OpenHands | `.openhands/skills/` | `~/.openhands/` |
| Pi | `.pi/skills/` | `~/.pi/` |
| Pochi | `.pochi/skills/` | `~/.pochi/` |
| Qoder | `.qoder/skills/` | `~/.qoder/` |
| Qwen Code | `.qwen/skills/` | `~/.qwen/` |
| Roo Code | `.roo/skills/` | `~/.roo/` |
| Trae | `.trae/skills/` | `~/.trae/` |
| Trae CN | `.trae/skills/` | `~/.trae/` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/windsurf/` |
| Zencoder | `.zencoder/skills/` | `~/.zencoder/` |

## Agent Detection Logic

The installer checks for agent-specific directories in the user's home folder.
It never scans the current working directory to avoid false positives from project
config files.

Detection categories:
- **Standard**: `~/.agentname/` (most agents)
- **XDG-based**: `~/.config/agentname/` (Amp, Crush, Goose, OpenCode, Gemini CLI)
- **Special cases**: Codex (`~/.codex/` + `/etc/codex`), Windsurf (`~/.codeium/windsurf/`)

## Agent Config Files

After installing skills, these agent config files should be updated:

| Agent | Config File | Format |
|-------|-------------|--------|
| Claude Code | `CLAUDE.md` | Markdown with skill references |
| Cursor | `.cursorrules` | Rules with skill paths |
| Windsurf | `.windsurfrules` | Rules with skill paths |
| Continue | `.continue/config.json` | JSON with skill paths |
| Cline | `.cline/settings.json` | JSON with skill references |

For agents without a documented config format, the skills in `.agents/skills/`
are sufficient — the agent discovers them automatically.
