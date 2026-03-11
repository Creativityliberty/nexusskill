const { neon } = require('@neondatabase/serverless');

async function fix() {
  const sql = neon("postgresql://neondb_owner:npg_4YpH9BMwmaCX@ep-plain-cell-ady4nccj-pooler.c-2.us-east-1.aws.neon.tech/neondb");
  
  // Reset all in_progress tasks to pending
  await sql`UPDATE tasks SET status = 'pending' WHERE status = 'in_progress'`;
  
  const tasks = await sql`SELECT id, mission_id, label, status FROM tasks ORDER BY id`;
  console.log("All tasks after reset:");
  tasks.forEach(t => console.log(`  Task #${t.id} [m_${t.mission_id}] ${t.label} => ${t.status}`));
}

fix().catch(console.error);
