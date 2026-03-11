import { GoogleGenAI } from "@google/genai";

const MODEL = "gemini-2.5-flash";

const SYSTEM_INSTRUCTION = `You are Nexus Hub's Mission Planner AI. Your role is to decompose a high-level mission objective into a structured list of executable tasks.

RULES:
1. Analyze the objective and generate between 3 and 10 tasks depending on complexity.
2. Each task MUST map to one of these available skills: skill-creator, mcp-builder, kernel-forge, ui-style-generator, swarm-orchestrator, api-designer, db-architect, test-engineer, devops-pipeline, security-auditor, docs-writer, performance-optimizer, data-pipeline, auth-flow, payment-integration, notification-system, search-engine, analytics-tracker, ci-cd-runner, code-reviewer, deploy-manager, monitoring-setup.
3. Tasks should have clear dependencies (order matters).
4. Return ONLY valid JSON. No markdown fences, no explanation.

OUTPUT FORMAT (JSON array):
[
  {
    "label": "Short action-oriented task description",
    "skill": "one-of-the-22-skills-above",
    "order": 0
  }
]

EXAMPLE for "Build a SaaS dashboard":
[
  {"label": "Design database schema for users and subscriptions", "skill": "db-architect", "order": 0},
  {"label": "Implement JWT authentication flow", "skill": "auth-flow", "order": 1},
  {"label": "Create REST API endpoints for dashboard data", "skill": "api-designer", "order": 2},
  {"label": "Build responsive dashboard UI components", "skill": "ui-style-generator", "order": 3},
  {"label": "Set up CI/CD and deploy pipeline", "skill": "devops-pipeline", "order": 4},
  {"label": "Write integration tests for API", "skill": "test-engineer", "order": 5}
]`;

export async function planMission(objective: string): Promise<Array<{ label: string; skill: string; order: number }>> {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY not configured");
  }

  const ai = new GoogleGenAI({ apiKey });

  const response = await ai.models.generateContent({
    model: MODEL,
    contents: `Mission objective: "${objective}"\n\nGenerate the task DAG.`,
    config: {
      systemInstruction: SYSTEM_INSTRUCTION,
      temperature: 0.3,
      maxOutputTokens: 2048,
    },
  });

  const text = response.text || "";
  
  // Clean response (remove potential markdown fences)
  const cleaned = text.replace(/```json\n?/g, "").replace(/```\n?/g, "").trim();
  
  const tasks = JSON.parse(cleaned);

  if (!Array.isArray(tasks) || tasks.length === 0) {
    throw new Error("LLM returned invalid task structure");
  }

  return tasks.map((t: { label?: string; skill?: string; order?: number }, i: number) => ({
    label: t.label || `Task ${i + 1}`,
    skill: t.skill || "skill-creator",
    order: t.order ?? i,
  }));
}
