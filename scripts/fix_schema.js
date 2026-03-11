const { neon } = require('@neondatabase/serverless');

async function fix() {
  const sql = neon("postgresql://neondb_owner:npg_4YpH9BMwmaCX@ep-plain-cell-ady4nccj-pooler.c-2.us-east-1.aws.neon.tech/neondb");
  
  console.log("Adding 'output' column...");
  await sql`ALTER TABLE tasks ADD COLUMN IF NOT EXISTS output TEXT`;
  
  const columns = await sql`SELECT column_name FROM information_schema.columns WHERE table_name = 'tasks'`;
  console.log("Current columns:", columns.map(c => c.column_name).join(', '));
}

fix().catch(console.error);
