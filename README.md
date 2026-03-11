# 🛰️ Nexus Hub — Nümtéma AI Foundry

**Mission Orchestration Engine for AI Agents**

Deploy, manage, and visualize AI-powered missions across 39+ coding agents with real-time execution tracking, interactive DAGs, and a cloud-native architecture.

---

## ⚡ Quick Start (Any Machine)

```bash
# 1. Clone
git clone https://github.com/Creativityliberty/nexusskill.git
cd nexusskill

# 2. Run setup wizard
node scripts/setup.js

# 3. Start dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) 🚀

---

## 🏗️ Architecture

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14 (App Router) + Tailwind + Shadcn UI |
| **API** | Next.js Route Handlers (`/api/v1/*`) |
| **Database** | Neon PostgreSQL (serverless) |
| **Hosting** | Vercel (auto-deploy from `main`) |
| **Agents** | 39 AI coding agents supported |

## 📦 Features

- **🎮 Mission Engine** — Play/Pause/Stop/Skip task execution with real-time DB persistence
- **🕸️ DAG Visualizer** — Animated SVG mission graphs with live status tracking
- **🔍 Skill Matrix** — 22 proprietary skills with tree view explorer
- **📜 Pipeline Log** — Terminal-style execution log
- **🔑 API Key Management** — Secure SHA-256 key generation
- **🛰️ Multi-Agent Installer** — Auto-detect and configure 39 AI agents

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/missions` | List all missions |
| `GET` | `/api/v1/missions/:id` | Get mission with tasks |
| `POST` | `/api/v1/mission/plan?goal=...` | Create mission + tasks |
| `GET` | `/api/v1/skills` | List synchronized skills |
| `POST` | `/api/v1/skills/sync` | Sync skills to database |
| `GET` | `/api/v1/stats` | Dashboard statistics |
| `GET` | `/api/v1/visualize` | DAG graph data |
| `PATCH` | `/api/v1/tasks/:id/status` | Update task status |
| `GET` | `/api/v1/keys` | List API keys |
| `POST` | `/api/v1/keys/generate?name=...` | Generate new API key |

## 🤖 Supported Agents (39)

Run `node scripts/install-skills.js` to auto-detect and configure:

**Universal** (read `.agents/skills/` directly): Amp, Codex, Gemini CLI, GitHub Copilot, Kimi Code, OpenCode

**Project-scoped** (symlinked): Antigravity, Claude Code, Cursor, Windsurf, Cline, Continue, Goose, Trae, Roo Code, and 24 more.

## 🚀 Deploy to Vercel

```bash
# One-time setup
npx vercel link

# Set environment variable
npx vercel env add DATABASE_URL

# Deploy
npx vercel --prod
```

## 📁 Project Structure

```
nexusskill/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Dashboard
│   │   ├── skills/page.tsx       # Skill Matrix
│   │   ├── keys/page.tsx         # API Key Management
│   │   ├── visualizer/page.tsx   # V-Mesh DAG Visualizer
│   │   ├── mission/[id]/page.tsx # Mission Detail + Engine
│   │   └── api/v1/              # All API routes
│   ├── components/
│   │   ├── skill-detail-modal.tsx
│   │   └── mission-modal.tsx
│   └── lib/
│       ├── db.ts                # Neon connection
│       └── skills-data.ts       # Skill catalog
├── scripts/
│   ├── setup.js                 # Setup wizard
│   └── install-skills.js        # 39-agent installer
└── .env.example                 # Environment template
```

---

© 2026 Nümtéma AI Foundry • Proprietary Technology
