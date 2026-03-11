const { neon } = require('@neondatabase/serverless');

async function test() {
  const sql = neon("postgresql://neondb_owner:npg_4YpH9BMwmaCX@ep-plain-cell-ady4nccj-pooler.c-2.us-east-1.aws.neon.tech/neondb");
  
  console.log("--- ANTIGRAVITY REMOTE TEST ---");
  
  // 1. Create a mission directly
  const goal = "Deep Audit of Nexus Hub Security & Architecture";
  const title = "Mission: Antigravity Elite Audit";
  
  const mission = await sql`
    INSERT INTO missions (title, description, status)
    VALUES (${title}, ${goal}, 'in_progress')
    RETURNING id
  `;
  
  const mid = mission[0].id;
  console.log(`Mission created: m_${mid}`);

  // 2. Add tasks
  const tasks = [
    { label: "[Antigravity] Scan API routes", skill: "mcp-builder" },
    { label: "[Antigravity] Verify Neon SSL pooler", skill: "kernel-forge" },
    { label: "[Antigravity] Optimize ReactFlow DAG", skill: "ui-style-generator" }
  ];

  for (let i = 0; i < tasks.length; i++) {
    await sql`
      INSERT INTO tasks (mission_id, label, skill, status, "order")
      VALUES (${mid}, ${tasks[i].label}, ${tasks[i].skill}, 'in_progress', ${i})
    `;
  }
  
  console.log("Tasks injected into Neural Mesh.");
  console.log("Test success. Check the Dashboard/Visualizer!");
}

test().catch(console.error);
