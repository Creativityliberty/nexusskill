import { NextResponse } from 'next/server';
import { getDB, initDB } from '@/lib/db';

export async function GET() {
  try {
    await initDB();
    const sql = getDB();
    const keys = await sql`SELECT id, name, created_at FROM api_keys ORDER BY created_at DESC`;
    return NextResponse.json(keys);
  } catch (error) {
    console.error("Keys GET error:", error);
    return NextResponse.json([]);
  }
}
