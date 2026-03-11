import { NextRequest, NextResponse } from 'next/server';
import { getDB, initDB } from '@/lib/db';
import { randomBytes, createHash } from 'crypto';

export async function POST(request: NextRequest) {
  try {
    await initDB();
    const sql = getDB();
    
    const { searchParams } = new URL(request.url);
    const name = searchParams.get('name') || 'New Key';
    
    // Generate secure key
    const rawKey = `nx_${randomBytes(32).toString('base64url')}`;
    const keyHash = createHash('sha256').update(rawKey).digest('hex');
    
    await sql`
      INSERT INTO api_keys (key_hash, name)
      VALUES (${keyHash}, ${name})
    `;
    
    return NextResponse.json({
      name: name,
      key: rawKey,
      message: "Store this key safely. It will not be shown again."
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    console.error("Key generate error:", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
