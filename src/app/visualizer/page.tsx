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
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Button } from "@/components/ui/button";
import { ChevronLeft, RefreshCw, Layers } from "lucide-react";
import Link from 'next/link';

export default function Visualizer() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);

  const fetchGraph = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/visualize');
      if (res.ok) {
        const data = await res.json();
        setNodes(data.nodes || []);
        setEdges(data.edges || []);
      }
    } catch (e) {
      console.error("Failed to load graph:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchGraph(); }, []);

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
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-blue-500" />
            <h1 className="text-lg font-bold tracking-tight text-neutral-100 uppercase italic">V-MESH CORE</h1>
          </div>
          <span className="text-[10px] font-mono bg-blue-900/10 text-blue-400/70 py-1 px-3 rounded-full border border-blue-900/30">
            SYSTEM STATUS: OPERATIONAL
          </span>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            className="border-neutral-800 text-neutral-400 hover:bg-neutral-900"
            onClick={fetchGraph}
            disabled={loading}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Sync Mesh
          </Button>
        </div>
      </header>

      <div className="flex-1 relative">
        {loading && nodes.length === 0 ? (
          <div className="flex items-center justify-center h-full text-neutral-500 italic bg-neutral-950">
            Fetching V-Mesh topology...
          </div>
        ) : nodes.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <div className="text-neutral-500 text-lg italic">The V-Mesh is empty. Start a new mission to generate nodes.</div>
            <Link href="/">
              <Button className="bg-blue-600 hover:bg-blue-700">
                Launch Initial Mission
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
            <Background color="#141414" gap={24} size={1} />
            <Controls className="!bg-neutral-900 !border-neutral-800 !text-neutral-400" />
            <MiniMap
              nodeColor={(n) => {
                if (n.id === 'hub') return '#6366f1';
                if (n.id.startsWith('m-')) return '#2563eb';
                return '#262626';
              }}
              maskColor="rgba(0, 0, 0, 0.7)"
              className="!bg-neutral-900 !border-neutral-800 !rounded-lg"
            />
          </ReactFlow>
        )}
      </div>

      <footer className="h-10 border-t border-neutral-800 bg-neutral-900/50 flex items-center justify-between px-6 text-[10px] text-neutral-500 font-mono">
        <span>&gt; VIZ ENGINE: V-MESH v2.1 • MODE: REAL-TIME SYNC</span>
        <div className="flex gap-4">
          <span>LATENCY: 12ms</span>
          <span className="text-blue-500/50">NÜMTÉMA SECURE LINK</span>
        </div>
      </footer>
    </div>
  );
}
