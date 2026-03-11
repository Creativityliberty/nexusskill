import { NextResponse } from 'next/server';
import { getDB, initDB } from '@/lib/db';

export async function GET() {
  try {
    await initDB();
    const sql = getDB();

    // Fetch all missions and their tasks
    const missions = await sql`SELECT * FROM missions ORDER BY created_at DESC`;
    const tasks = await sql`SELECT * FROM tasks ORDER BY mission_id, "order"`;

    const nodes: any[] = [
      {
        id: 'hub',
        position: { x: 400, y: 0 },
        data: { label: '🛰️ NEXUS HUB' },
        type: 'input',
        style: {
          background: 'linear-gradient(135deg, #1e40af, #7c3aed)',
          color: '#fff',
          border: '2px solid #818cf8',
          borderRadius: '12px',
          padding: '12px 24px',
          fontWeight: 'bold',
          fontSize: '14px',
          boxShadow: '0 0 20px rgba(99,102,241,0.3)',
        }
      }
    ];

    const edges: any[] = [];

    missions.forEach((m, i) => {
      const col = i % 3;
      const row = Math.floor(i / 3);
      const x = 100 + col * 350;
      const y = 140 + row * 220;
      
      const missionTasks = tasks.filter(t => t.mission_id === m.id);

      // Mission node
      nodes.push({
        id: `m-${m.id}`,
        position: { x, y },
        data: { label: m.title },
        style: {
          background: '#1e3a5f',
          border: '1px solid #2563eb',
          borderRadius: '8px',
          padding: '10px',
          color: '#fff',
          fontWeight: 'bold',
          fontSize: '12px',
          minWidth: '200px'
        }
      });

      edges.push({
        id: `hub-m${m.id}`,
        source: 'hub',
        target: `m-${m.id}`,
        animated: true,
        style: { stroke: '#2563eb' }
      });

      // Task nodes
      missionTasks.forEach((t, ti) => {
        const tx = x - 50 + ti * 100;
        const ty = y + 150;
        
        nodes.push({
          id: `t-${t.id}`,
          position: { x: tx, y: ty },
          data: { label: t.label },
          style: {
            background: '#171717',
            border: '1px solid #333',
            borderRadius: '6px',
            padding: '5px',
            fontSize: '10px',
            color: '#a3a3a3'
          }
        });

        edges.push({
          id: `e-${m.id}-${t.id}`,
          source: `m-${m.id}`,
          target: `t-${t.id}`,
          style: { stroke: '#444' }
        });
      });
    });

    return NextResponse.json({ nodes, edges });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
