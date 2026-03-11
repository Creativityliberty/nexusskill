const { GoogleGenAI } = require("@google/genai");

const SYSTEM_INSTRUCTION = `You are Nexus Hub's Mission Planner AI. Your role is to decompose a high-level mission objective into a structured list of executable tasks.

RULES:
1. Analyze the objective and generate between 3 and 10 tasks depending on complexity.
2. Each task MUST map to one of these available skills: skill-creator, mcp-builder, kernel-forge, ui-style-generator, swarm-orchestrator, api-designer, db-architect, test-engineer, devops-pipeline, security-auditor, docs-writer, performance-optimizer, data-pipeline, auth-flow, payment-integration, notification-system, search-engine, analytics-tracker, ci-cd-runner, code-reviewer, deploy-manager, monitoring-setup.
3. Return ONLY valid JSON. No markdown fences, no explanation.

OUTPUT FORMAT (JSON array):
[
  {"label": "Short task description", "skill": "skill-name", "order": 0}
]`;

async function testPlanner() {
  const ai = new GoogleGenAI({ apiKey: "AIzaSyCZ0tK6IC10U2eNzFgTH6ZEuVVmt22GfXg" });

  console.log("🧠 Testing Gemini Dynamic Planner...\n");

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: 'Mission objective: "Build a fintech SaaS dashboard with Stripe integration, user analytics, and real-time notifications"\n\nGenerate the task DAG.',
    config: {
      systemInstruction: SYSTEM_INSTRUCTION,
      temperature: 0.3,
      maxOutputTokens: 2048,
    },
  });

  const text = response.text || "";
  const cleaned = text.replace(/```json\n?/g, "").replace(/```\n?/g, "").trim();
  
  console.log("📋 Raw Gemini Response:");
  console.log(cleaned);
  
  const tasks = JSON.parse(cleaned);
  console.log(`\n✅ Gemini generated ${tasks.length} tasks:\n`);
  tasks.forEach((t, i) => {
    console.log(`  ${i+1}. [${t.skill}] ${t.label}`);
  });
}

testPlanner().catch(console.error);
