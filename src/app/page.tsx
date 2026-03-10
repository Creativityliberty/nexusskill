"use client"

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { 
  Rocket, 
  ShieldCheck, 
  Cpu, 
  BarChart3, 
  Key, 
  Box, 
  Plus,
  Terminal,
  Layers
} from "lucide-react";
import Link from "next/link";
import { useState, useEffect } from "react";

interface Mission {
  id: number;
  title: string;
  description: string;
  status: string;
  created_at: string;
}

export default function Dashboard() {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchMissions() {
      try {
        const response = await fetch('/api/v1/missions', {
          headers: { 'X-Nexus-Key': 'development_key' } // Default key for dev
        });
        if (response.ok) {
          const data = await response.json();
          setMissions(data);
        }
      } catch (error) {
        console.error("Failed to fetch missions:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchMissions();
  }, []);
  const createMission = async () => {
    const goal = prompt("Define your Mission Objective:");
    if (!goal) return;

    try {
      const response = await fetch(`/api/v1/mission/plan?goal=${encodeURIComponent(goal)}`, {
        method: 'POST',
        headers: { 'X-Nexus-Key': 'development_key' }
      });
      if (response.ok) {
        const newMission = await response.json();
        // Refresh missions
        const res = await fetch('/api/v1/missions', {
          headers: { 'X-Nexus-Key': 'development_key' }
        });
        if (res.ok) setMissions(await res.json());
      }
    } catch (error) {
      console.error("Failed to create mission:", error);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 p-6 font-sans">
      <header className="flex justify-between items-center mb-10 border-b border-neutral-800 pb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center shadow-[0_0_20px_rgba(37,99,235,0.3)]">
            <Layers className="text-white w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">NEXUS HUB</h1>
            <p className="text-sm text-neutral-400">N\u00fcmtema AI FOUNDRY \u2022 Mission Engine v1.0</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="outline" className="border-neutral-800 hover:bg-neutral-900">
            <Key className="mr-2 h-4 w-4" /> API Keys
          </Button>
          <Button 
            onClick={createMission}
            className="bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-900/20"
          >
            <Plus className="mr-2 h-4 w-4" /> New Mission
          </Button>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar Summary */}
        <div className="lg:col-span-1 space-y-6">
          <Card className="bg-neutral-900/50 border-neutral-800 backdrop-blur-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-neutral-400">Active Missions</CardTitle>
              <div className="text-3xl font-bold">{missions.length}</div>
            </CardHeader>
            <CardContent>
              <div className="h-1.5 w-full bg-neutral-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]" 
                  style={{ width: `${Math.min((missions.length / 20) * 100, 100)}%` }}
                ></div>
              </div>
              <p className="text-xs text-neutral-500 mt-2">{((missions.length / 20) * 100).toFixed(0)}% of monthly target projects</p>
            </CardContent>
          </Card>

          <Card className="bg-neutral-900/50 border-neutral-800 backdrop-blur-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-neutral-400">Skills Synchronized</CardTitle>
              <div className="text-3xl font-bold text-green-500">22</div>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-neutral-500">Across 8 configured agents</p>
            </CardContent>
          </Card>

          <nav className="space-y-1">
            <Link href="/">
              <Button variant="ghost" className="w-full justify-start text-neutral-400 hover:text-white hover:bg-neutral-900">
                <Rocket className="mr-3 h-4 w-4" /> Missions
              </Button>
            </Link>
            <Link href="/skills">
              <Button variant="ghost" className="w-full justify-start text-neutral-400 hover:text-white hover:bg-neutral-900">
                <Cpu className="mr-3 h-4 w-4" /> Skill Matrix
              </Button>
            </Link>
            <Button variant="ghost" className="w-full justify-start text-neutral-400 hover:text-white hover:bg-neutral-900">
              <ShieldCheck className="mr-3 h-4 w-4" /> Quality Gates
            </Button>
            <Button variant="ghost" className="w-full justify-start text-neutral-400 hover:text-white hover:bg-neutral-900">
              <BarChart3 className="mr-3 h-4 w-4" /> Analytics
            </Button>
          </nav>
        </div>

        {/* Main Content Area */}
        <div className="lg:col-span-3 space-y-6">
          <Tabs defaultValue="active" className="w-full">
            <div className="flex justify-between items-center mb-4">
              <TabsList className="bg-neutral-900 border border-neutral-800">
                <TabsTrigger value="active" className="data-[state=active]:bg-neutral-800">Active</TabsTrigger>
                <TabsTrigger value="completed" className="data-[state=active]:bg-neutral-800">Completed</TabsTrigger>
                <TabsTrigger value="archived" className="data-[state=active]:bg-neutral-800">Archived</TabsTrigger>
              </TabsList>
            </div>
            
            <TabsContent value="active" className="mt-0 space-y-4">
              <Card className="bg-neutral-900/50 border-neutral-800 overflow-hidden backdrop-blur-md">
                <div className="p-0">
                  <Table>
                    <TableHeader className="bg-neutral-900/80">
                      <TableRow className="border-neutral-800 hover:bg-neutral-900/50">
                        <TableHead className="w-[300px] text-neutral-400">Mission</TableHead>
                        <TableHead className="text-neutral-400">Status</TableHead>
                        <TableHead className="text-neutral-400">Agent Focus</TableHead>
                        <TableHead className="text-right text-neutral-400">Created</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {loading ? (
                        <TableRow>
                          <TableCell colSpan={4} className="text-center py-10 text-neutral-500 italic">
                            Synchronizing with Neural Mesh...
                          </TableCell>
                        </TableRow>
                      ) : missions.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={4} className="text-center py-10 text-neutral-500">
                            No active missions. Trigger a new one to begin orchestration.
                          </TableCell>
                        </TableRow>
                      ) : (
                        missions.map((m) => (
                          <TableRow key={m.id} className="border-neutral-800 hover:bg-neutral-900/50">
                            <TableCell className="font-medium">
                              <div className="flex flex-col">
                                <span>{m.title}</span>
                                <span className="text-xs text-neutral-500">mission_id: m_{m.id}</span>
                              </div>
                            </TableCell>
                            <TableCell>
                              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${
                                m.status === 'planned' ? 'bg-blue-900/30 text-blue-400 border-blue-800/50' : 
                                m.status === 'completed' ? 'bg-green-900/30 text-green-400 border-green-800/50' : 
                                'bg-neutral-900/30 text-neutral-400 border-neutral-800/50'
                              }`}>
                                {m.status.toUpperCase()}
                              </span>
                            </TableCell>
                            <TableCell className="text-neutral-300">Nexus Auto-Pilot</TableCell>
                            <TableCell className="text-right text-neutral-500 font-mono text-xs">
                              {new Date(m.created_at).toLocaleDateString()}
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </div>
              </Card>

              {/* Console/Activity View */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="bg-neutral-900/50 border-neutral-800 h-[300px] flex flex-col">
                  <CardHeader className="pb-2 border-b border-neutral-800 bg-neutral-900/80">
                    <CardTitle className="text-xs font-mono flex items-center gap-2">
                       <Terminal className="h-3 w-3 text-blue-400" /> SYSTEM CONSOLE
                    </CardTitle>
                  </CardHeader>
                  <ScrollArea className="flex-1 p-4 font-mono text-[11px] leading-relaxed">
                    <div className="text-neutral-500">[09:12:01] Initializing Nexus Mission Orchestrator...</div>
                    <div className="text-blue-400">[09:12:02] Fetching skills from aiskills-repo...</div>
                    <div className="text-green-400">[09:12:03] SUCCESS: 22 skills synchronized.</div>
                    <div className="text-neutral-400">[09:12:05] Agent 'Claude-3.7-Sonnet' connected via Hub API.</div>
                    <div className="text-yellow-400">[09:13:00] MISSION START: SaaS Fintech Dashboard</div>
                    <div className="text-neutral-500">[09:13:02] Triggering skill: 'skill-creator'...</div>
                  </ScrollArea>
                </Card>

                <Card className="bg-neutral-900/50 border-neutral-800 h-[300px] p-6 flex flex-col items-center justify-center text-center">
                  <div className="w-16 h-16 bg-blue-900/10 rounded-full flex items-center justify-center mb-4">
                    <Box className="text-blue-500 w-8 h-8" />
                  </div>
                  <h3 className="font-semibold text-neutral-300 mb-1">Interactive Visualizer</h3>
                  <p className="text-sm text-neutral-500 max-w-[200px] mb-4">
                    Explore mission DAGs and task relationships in real-time.
                  </p>
                  <Link href="/visualizer">
                    <Button variant="outline" size="sm" className="border-blue-900/50 text-blue-400 hover:bg-blue-900/20">
                      Open Visualizer
                    </Button>
                  </Link>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>

      <footer className="mt-12 text-center text-neutral-600 text-xs border-t border-neutral-900 pt-8">
        &copy; 2026 N\u00fcmtema AI FOUNDRY \u2022 All Rights Reserved \u2022 Proprietary Technology
      </footer>
    </div>
  );
}
