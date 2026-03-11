"use client"

import React, { useCallback, useEffect, useState } from 'react';
import ReactFlow, {
  useNodesState,
  useEdgesState,
  addEdge,
  Background,
  Controls,
  MiniMap,
  Connection,
  Edge,
  Node,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Button } from "@/components/ui/button";
import { ChevronLeft, RefreshCw, Maximize2 } from "lucide-react";
import Link from 'next/link';

interface Mission {
  id: number;
  title: string;
  description: string;
  status: string;
  created_at: string;
}

const statusColors: Record<string, { bg: string; border: string; text: string }> = {
  planned: { bg: '#1e3a5f', border: '#2563eb', text: '#60a5fa' },
  in_progress: { bg: '#3b2f1a', border: '#d97706', text: '#fbbf24' },
  completed: { bg: '#1a3b2f', border: '#16a34a', text: '#4ade80' },
  failed: { bg: '#3b1a1a', border: '#dc2626', text: '#f87171' },
};

function buildDAG(missions: Mission[]) {
  const nodes: Node[] = [
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

  const edges: Edge[] = [];

  missions.forEach((m, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 100 + col * 350;
    const y = 120 + row * 180;
    const colors = statusColors[m.status] || statusColors.planned;

    // Mission node
    nodes.push({
      id: `m-${m.id}`,
      position: { x, y },
      data: {
        label: (
          <div style={{ textAlign: 'left' }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold', color: colors.text, marginBottom: '4px' }}>
              {m.title}
            </div>
            <div style={{ fontSize: '10px', color: '#737373', fontFamily: 'monospace' }}>
              m_{m.id} • {m.status.toUpperCase()}
            </div>
          </div>
        ),
      },
      style: {
        background: colors.bg,
        border: `1px solid ${colors.border}`,
        borderRadius: '8px',
        padding: '10px 14px',
        minWidth: '220px',
      }
    });

    // Hub → Mission edge
    edges.push({
      id: `hub-m${m.id}`,
      source: 'hub',
      target: `m-${m.id}`,
      animated: m.status === 'in_progress' || m.status === 'planned',
      style: { stroke: colors.border, strokeWidth: 2 },
    });

    // Task nodes for each mission
    const tasks = [
      { id: `t-${m.id}-1`, label: '📋 Research', skill: 'context-builder' },
      { id: `t-${m.id}-2`, label: '⚙️ Execute', skill: 'skill-creator' },
      { id: `t-${m.id}-3`, label: '✅ Validate', skill: 'review-pr' },
    ];

    tasks.forEach((task, ti) => {
      nodes.push({
        id: task.id,
        position: { x: x - 60 + ti * 110, y: y + 130 },
        data: {
          label: (
            <div style={{ textAlign: 'center', fontSize: '10px' }}>
              <div>{task.label}</div>
              <div style={{ color: '#525252', fontFamily: 'monospace', fontSize: '9px' }}>{task.skill}</div>
            </div>
          ),
        },
        style: {
          background: '#171717',
          border: '1px solid #262626',
          borderRadius: '6px',
          padding: '6px 8px',
          fontSize: '10px',
        }
      });

      edges.push({
        id: `${m.id}-${task.id}`,
        source: `m-${m.id}`,
        target: task.id,
        style: { stroke: '#333', strokeDasharray: '4 2' },
      });

      // Chain tasks
      if (ti > 0) {
        edges.push({
          id: `chain-${m.id}-${ti}`,
          source: tasks[ti - 1].id,
          target: task.id,
          animated: false,
          style: { stroke: '#262626' },
        });
      }
    });
  });

  return { nodes, edges };
}

export default function Visualizer() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAndBuild = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/missions');
      if (res.ok) {
        const data = await res.json();
        setMissions(data);
        const dag = buildDAG(data);
        setNodes(dag.nodes);
        setEdges(dag.edges);
      }
    } catch (e) {
      console.error("Failed to load missions for visualizer:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAndBuild(); }, []);

  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="h-screen w-full bg-neutral-950 flex flex-col">
      <header className="h-16 border-b border-neutral-800 flex items-center justify-between px-6 bg-neutral-900/50 backdrop-blur-md z-10">
        <div className="flex items-center gap-4">
          <Link href="/">
            <Button variant="ghost" size="icon" className="text-neutral-400 hover:bg-neutral-800">
              <ChevronLeft className="h-5 w-5" />
            </Button>
          </Link>
          <h1 className="text-lg font-bold tracking-tight text-neutral-100">MISSION VISUALIZER</h1>
          <span className="text-xs font-mono bg-blue-900/30 text-blue-400 px-2 py-0.5 rounded border border-blue-800/50">
            {missions.length} missions • {missions.length * 3} tasks
          </span>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            className="border-neutral-800 text-neutral-400"
            onClick={fetchAndBuild}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </header>

      <div className="flex-1 relative">
        {loading && missions.length === 0 ? (
          <div className="flex items-center justify-center h-full text-neutral-500 italic">
            Loading mission graph from Neural Mesh...
          </div>
        ) : missions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <div className="text-neutral-500 text-lg">No missions to visualize</div>
            <Link href="/">
              <Button className="bg-blue-600 hover:bg-blue-700">
                Create a Mission First
              </Button>
            </Link>
          </div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            fitView
            className="bg-neutral-950"
          >
            <Background color="#1a1a1a" gap={20} size={1} />
            <Controls className="!bg-neutral-900 !border-neutral-800 !text-neutral-400" />
            <MiniMap
              nodeColor={(n) => {
                if (n.id === 'hub') return '#6366f1';
                if (n.id.startsWith('m-')) return '#2563eb';
                return '#262626';
              }}
              className="!bg-neutral-900 !border-neutral-800"
            />
          </ReactFlow>
        )}
      </div>

      <footer className="h-10 border-t border-neutral-800 bg-neutral-900/50 flex items-center justify-between px-6 text-[10px] text-neutral-500 font-mono">
        <span>&gt; DAG Visualizer Engine: ReactFlow v11 • Mode: Live Orchestration</span>
        <span>NÜMTÉMA PROPRIETARY • {new Date().toLocaleDateString()}</span>
      </footer>
    </div>
  );
}
