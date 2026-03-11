"use client"

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  ChevronLeft, 
  Search, 
  RefreshCw,
  Code,
  Terminal,
  Cpu,
  Layers
} from "lucide-react";
import Link from 'next/link';

interface Skill {
  id: number;
  name: string;
  description: string;
  last_sync: string;
}

export default function SkillMatrix() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  const fetchSkills = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/skills', {
        headers: { 'X-Nexus-Key': 'development_key' }
      });
      if (response.ok) {
        setSkills(await response.json());
      }
    } catch (error) {
      console.error("Failed to fetch skills:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      const response = await fetch('/api/v1/skills/sync', {
        method: 'POST',
        headers: { 'X-Nexus-Key': 'development_key' }
      });
      if (response.ok) {
        const text = await response.text();
        try {
          const data = JSON.parse(text);
          alert(data.message || "Skills synchronized!");
        } catch (e) {
          console.error("JSON Parse error:", text);
          alert(`Sync partly success but invalid JSON: ${text.substring(0, 100)}...`);
        }
        await fetchSkills();
      } else {
        const text = await response.text();
        console.error("Sync error response:", text);
        alert(`Sync failed (Server Error): ${text.substring(0, 100)}...`);
      }
    } catch (error) {
      console.error("Sync failed:", error);
    } finally {
      setSyncing(false);
    }
  };

  useEffect(() => {
    fetchSkills();
  }, []);

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 p-6 font-sans">
      <header className="flex justify-between items-center mb-10 border-b border-neutral-800 pb-6">
        <div className="flex items-center gap-3">
          <Link href="/">
            <Button variant="ghost" size="icon" className="text-neutral-400 hover:text-white">
              <ChevronLeft className="h-6 w-6" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">SKILL MATRIX</h1>
            <p className="text-sm text-neutral-400">Synchronized Agent Capabilities</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-500" />
            <input 
              type="text" 
              placeholder="Search skills..." 
              className="bg-neutral-900 border border-neutral-800 rounded-md pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 w-64"
            />
          </div>
          <Button 
            onClick={handleSync} 
            disabled={syncing}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync Repository'}
          </Button>
        </div>
      </header>

      <main className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full py-20 text-center text-neutral-500 italic">
            Fetching agent neuro-nodes...
          </div>
        ) : skills.length === 0 ? (
          <div className="col-span-full py-20 text-center text-neutral-500">
            No skills found in the mesh. Trigger a sync to import from aiskills-repo.
          </div>
        ) : (
          skills.map((skill) => (
            <Card key={skill.id} className="bg-neutral-900/50 border-neutral-800 hover:border-blue-900/50 transition-all hover:bg-neutral-900 group">
              <CardHeader className="pb-3 px-6 pt-6">
                <div className="flex justify-between items-start mb-2">
                  <div className="w-10 h-10 bg-neutral-800 rounded flex items-center justify-center group-hover:bg-blue-900/20 transition-colors">
                    <Code className="text-blue-500 w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-mono text-neutral-600 uppercase tracking-widest">
                    v1.0.0
                  </span>
                </div>
                <CardTitle className="text-lg font-bold">{skill.name}</CardTitle>
                <CardDescription className="text-neutral-500 text-sm line-clamp-2 mt-1">
                  {skill.description || "No description provided."}
                </CardDescription>
              </CardHeader>
              <CardContent className="px-6 pb-6">
                <div className="flex gap-2 mb-4">
                  <span className="px-2 py-0.5 bg-green-900/20 text-green-500 text-[10px] rounded border border-green-800/30">
                    Proprietary
                  </span>
                  <span className="px-2 py-0.5 bg-neutral-800 text-neutral-400 text-[10px] rounded">
                    L3 Agent
                  </span>
                </div>
                <div className="flex items-center justify-between pt-4 border-t border-neutral-800/50">
                  <span className="text-[10px] text-neutral-600 font-mono">
                    SYNC: {new Date(skill.last_sync).toLocaleDateString()}
                  </span>
                  <Button variant="link" className="h-auto p-0 text-blue-500 text-xs hover:text-blue-400">
                    View Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </main>

      <footer className="mt-12 text-center text-neutral-600 text-[10px] font-mono border-t border-neutral-900 pt-8">
        HUB CORE: skill-ingestor v1.2 \u2022 AGENT MESH: ACTIVE \u2022 N\u00dcMTEMA PROPERTY
      </footer>
    </div>
  );
}
