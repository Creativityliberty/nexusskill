const { neon } = require('@neondatabase/serverless');
async function check() {
  const sql = neon("postgresql://neondb_owner:npg_4YpH9BMwmaCX@ep-plain-cell-ady4nccj-pooler.c-2.us-east-1.aws.neon.tech/neondb");
  const res = await sql`SELECT column_name FROM information_schema.columns WHERE table_name = 'tasks'`;
  console.log("Columns in 'tasks' table:");
  res.forEach(r => console.log(` - ${r.column_name}`));
  
  const sample = await sql`SELECT id, mission_id, label, status, output FROM tasks ORDER BY id DESC LIMIT 5`;
  console.log("\nRecent tasks with output:");
  sample.forEach(s => console.log(` Task #${s.id} (m_${s.mission_id}) [${s.status}] ${s.label} -> Output size: ${s.output ? s.output.length : 0}`));
}
check().catch(console.error);
