"use client"

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
import SkillDetailModal from "@/components/skill-detail-modal";
import { SKILLS_CATALOG, type SkillData } from "@/lib/skills-data";

interface SkillFromDB {
  id: number;
  name: string;
  description: string;
  last_sync: string;
}

export default function SkillMatrix() {
  const [skills, setSkills] = useState<SkillFromDB[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [search, setSearch] = useState("");
  const [selectedSkill, setSelectedSkill] = useState<SkillData | null>(null);

  const fetchSkills = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/skills');
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
      const response = await fetch('/api/v1/skills/sync', { method: 'POST' });
      if (response.ok) {
        const data = await response.json();
        alert(data.message || "Skills synchronized!");
        await fetchSkills();
      } else {
        const text = await response.text();
        alert(`Sync failed: ${text.substring(0, 150)}`);
      }
    } catch (error) {
      console.error("Sync failed:", error);
    } finally {
      setSyncing(false);
    }
  };

  const openSkillDetail = (skillName: string) => {
    const catalogSkill = SKILLS_CATALOG.find(s => s.name === skillName);
    if (catalogSkill) {
      setSelectedSkill(catalogSkill);
    }
  };

  useEffect(() => { fetchSkills(); }, []);

  const filteredSkills = skills.filter(s =>
    s.name.toLowerCase().includes(search.toLowerCase()) ||
    s.description?.toLowerCase().includes(search.toLowerCase())
  );

  const iconForSkill = (name: string) => {
    if (name.includes("agent") || name.includes("orchestra")) return <Cpu className="text-purple-500 w-5 h-5" />;
    if (name.includes("kernel") || name.includes("flow")) return <Layers className="text-orange-500 w-5 h-5" />;
    if (name.includes("mcp") || name.includes("nano")) return <Terminal className="text-green-500 w-5 h-5" />;
    return <Code className="text-blue-500 w-5 h-5" />;
  };

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
              value={search}
              onChange={(e) => setSearch(e.target.value)}
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
        ) : filteredSkills.length === 0 ? (
          <div className="col-span-full py-20 text-center text-neutral-500">
            {search ? `No skills matching "${search}"` : "No skills found. Trigger a sync to import."}
          </div>
        ) : (
          filteredSkills.map((skill, idx) => (
            <Card
              key={skill.id || idx}
              className="bg-neutral-900/50 border-neutral-800 hover:border-blue-900/50 transition-all hover:bg-neutral-900 group cursor-pointer"
              onClick={() => openSkillDetail(skill.name)}
            >
              <CardHeader className="pb-3 px-6 pt-6">
                <div className="flex justify-between items-start mb-2">
                  <div className="w-10 h-10 bg-neutral-800 rounded flex items-center justify-center group-hover:bg-blue-900/20 transition-colors">
                    {iconForSkill(skill.name)}
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
                    SYNC: {skill.last_sync ? new Date(skill.last_sync).toLocaleDateString() : "N/A"}
                  </span>
                  <span className="text-blue-500 text-xs group-hover:text-blue-400 transition-colors">
                    View Details →
                  </span>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </main>

      {selectedSkill && (
        <SkillDetailModal
          skill={selectedSkill}
          onClose={() => setSelectedSkill(null)}
        />
      )}

      <footer className="mt-12 text-center text-neutral-600 text-[10px] font-mono border-t border-neutral-900 pt-8">
        HUB CORE: skill-ingestor v1.2 • AGENT MESH: ACTIVE • NÜMTEMA PROPERTY
      </footer>
    </div>
  );
}
