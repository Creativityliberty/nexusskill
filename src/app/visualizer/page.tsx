"use client"

import React, { useCallback } from 'react';
import ReactFlow, { 
  useNodesState, 
  useEdgesState, 
  addEdge, 
  Background, 
  Controls,
  Connection,
  Edge
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Button } from "@/components/ui/button";
import { ChevronLeft, Save, Share2 } from "lucide-react";
import Link from 'next/link';

const initialNodes = [
  { id: '1', position: { x: 0, y: 0 }, data: { label: 'Start: Objective' }, type: 'input' },
  { id: '2', position: { x: 200, y: 100 }, data: { label: 'Research Phase (Skill: context-builder)' } },
  { id: '3', position: { x: 400, y: 200 }, data: { label: 'Implementation (Skill: skill-creator)' } },
  { id: '4', position: { x: 600, y: 300 }, data: { label: 'End: Quality Pass' }, type: 'output' },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e2-3', source: '2', target: '3', animated: true },
  { id: 'e3-4', source: '3', target: '4', animated: true },
];

export default function Visualizer() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="h-screen w-full bg-neutral-950 flex flex-col">
      {/* Header */}
      <header className="h-16 border-b border-neutral-800 flex items-center justify-between px-6 bg-neutral-900/50 backdrop-blur-md z-10">
        <div className="flex items-center gap-4">
          <Link href="/">
            <Button variant="ghost" size="icon" className="text-neutral-400 hover:bg-neutral-800">
              <ChevronLeft className="h-5 w-5" />
            </Button>
          </Link>
          <h1 className="text-lg font-bold tracking-tight text-neutral-100">MISSION VISUALIZER</h1>
          <span className="text-xs font-mono bg-blue-900/30 text-blue-400 px-2 py-0.5 rounded border border-blue-800/50">
            m_a782b
          </span>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" className="border-neutral-800 text-neutral-400">
            <Share2 className="mr-2 h-4 w-4" /> Share
          </Button>
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
            <Save className="mr-2 h-4 w-4" /> Save DAG
          </Button>
        </div>
      </header>

      {/* React Flow Area */}
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          colorMode="dark"
        >
          <Background color="#171717" gap={16} />
          <Controls />
        </ReactFlow>
      </div>

      <footer className="h-10 border-t border-neutral-800 bg-neutral-900/50 flex items-center px-6 text-[10px] text-neutral-500 font-mono">
        &gt; DAG Visualizer Engine: ReactFlow v11 \u2022 Mode: Interactive Orchestration
      </footer>
    </div>
  );
}
