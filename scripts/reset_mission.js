const { neon } = require('@neondatabase/serverless');

async function reset() {
  const sql = neon("postgresql://neondb_owner:npg_4YpH9BMwmaCX@ep-plain-cell-ady4nccj-pooler.c-2.us-east-1.aws.neon.tech/neondb");
  
  console.log("Resetting Mission #8 tasks...");
  await sql`UPDATE tasks SET status = 'pending', output = NULL WHERE mission_id = 8`;
  
  const tasks = await sql`SELECT id, label, status FROM tasks WHERE mission_id = 8`;
  console.log("Mission #8 tasks state:");
  tasks.forEach(t => console.log(` - ${t.label}: ${t.status}`));
}

reset().catch(console.error);
