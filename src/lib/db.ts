import { neon } from '@neondatabase/serverless';

export function getDB() {
  const url = process.env.DATABASE_URL;
  if (!url) {
    throw new Error("DATABASE_URL is not set");
  }
  return neon(url);
}

// Initialize tables if they don't exist
export async function initDB() {
  const sql = getDB();
  await sql`
    CREATE TABLE IF NOT EXISTS skills (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) UNIQUE NOT NULL,
      description TEXT,
      content TEXT,
      last_sync TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )
  `;
  await sql`
    CREATE TABLE IF NOT EXISTS missions (
      id SERIAL PRIMARY KEY,
      title VARCHAR(255) NOT NULL,
      description TEXT,
      status VARCHAR(50) DEFAULT 'planned',
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )
  `;
  await sql`
    CREATE TABLE IF NOT EXISTS api_keys (
      id SERIAL PRIMARY KEY,
      key_hash VARCHAR(255) UNIQUE NOT NULL,
      name VARCHAR(255) DEFAULT 'Default Key',
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )
  `;
}
