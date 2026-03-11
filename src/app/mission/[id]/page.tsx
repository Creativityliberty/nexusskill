"use client"

import { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import {
  ChevronLeft, Play, Pause, Square, SkipForward, RotateCcw,
  Download, Copy, CheckCircle2, Layers, Terminal, Clock,
  FileText, Package, AlertCircle
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

interface Task {
  id: number;
  mission_id: number;
  label: string;
  skill: string;
  status: string;
  order: number;
}

interface Mission {
  id: number;
  title: string;
  description: string;
  status: string;
  created_at: string;
  tasks: Task[];
}

// ═══ ENGINE HOOK ═══
function useEngine(tasks: Task[], setTasks: (fn: (prev: Task[]) => Task[]) => void) {
  const [state, setState] = useState<"idle"|"running"|"paused"|"done">("idle");
  const [curId, setCurId] = useState<number|null>(null);
  const [log, setLog] = useState<{ts:string;msg:string;type:string;id:number}[]>([]);
  const [elapsed, setElapsed] = useState(0);
  const iRef = useRef<NodeJS.Timeout|null>(null);
  const tRef = useRef<NodeJS.Timeout|null>(null);
  const t0 = useRef(0);
  const pBase = useRef(0);

  const addLog = useCallback((msg: string, type = "info") => {
    const ts = new Date().toLocaleTimeString("fr-FR", { hour12: false });
    setLog(p => [...p.slice(-79), { ts, msg, type, id: Date.now() + Math.random() }]);
  }, []);

  const kill = () => { if (iRef.current) clearInterval(iRef.current); if (tRef.current) clearInterval(tRef.current); };

  const clock = () => {
    const b = pBase.current;
    t0.current = Date.now();
    tRef.current = setInterval(() => setElapsed(b + Date.now() - t0.current), 100);
  };

  const nextPending = (arr: Task[]) => arr.find(t => t.status === "pending");

  const updateTaskStatus = async (taskId: number, status: string) => {
    try {
      await fetch(`/api/v1/tasks/${taskId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
    } catch (e) { console.error("Failed to update task status:", e); }
  };

  const tick = useCallback(() => {
    setTasks((prev: Task[]) => {
      const running = prev.find(t => t.status === "running");
      if (running) {
        addLog(`✓  Task #${running.id} — ${running.label}`, "success");
        updateTaskStatus(running.id, "done");
        const updated = prev.map(t => t.id === running.id ? { ...t, status: "done" } : t);
        const next = nextPending(updated);
        if (!next) {
          setState("done"); setCurId(null); kill();
          addLog("▪ Pipeline complete. All tasks resolved.", "success");
          return updated;
        }
        addLog(`▶  Task #${next.id} — ${next.label}`, "run");
        setCurId(next.id);
        updateTaskStatus(next.id, "running");
        return updated.map(t => t.id === next.id ? { ...t, status: "running" } : t);
      }
      const next = nextPending(prev);
      if (!next) { setState("done"); setCurId(null); kill(); return prev; }
      addLog(`▶  Task #${next.id} — ${next.label}`, "run");
      setCurId(next.id);
      updateTaskStatus(next.id, "running");
      return prev.map(t => t.id === next.id ? { ...t, status: "running" } : t);
    });
  }, [addLog]);

  const play = useCallback(() => {
    if (state === "done") return;
    setState("running");
    addLog("▪ Engine started", "info");
    clock();
    iRef.current = setInterval(tick, 2500);
  }, [state, addLog, tick]);

  const pause = useCallback(() => {
    if (state !== "running") return;
    kill();
    pBase.current += Date.now() - t0.current;
    setState("paused");
    addLog("▪ Paused", "warn");
    setTasks(p => p.map(t => t.status === "running" ? { ...t, status: "paused" } : t));
  }, [state, addLog]);

  const resume = useCallback(() => {
    if (state !== "paused") return;
    setState("running");
    addLog("▪ Resumed", "info");
    setTasks(p => p.map(t => t.status === "paused" ? { ...t, status: "running" } : t));
    clock();
    iRef.current = setInterval(tick, 2500);
  }, [state, addLog, tick]);

  const stop = useCallback(() => {
    kill();
    setState("idle");
    setCurId(null);
    addLog("▪ Stopped. Progress preserved.", "warn");
    setTasks(p => p.map(t => ["running", "paused"].includes(t.status) ? { ...t, status: "pending" } : t));
  }, [addLog]);

  const skip = useCallback(() => {
    if (!curId) return;
    addLog(`⏭  Skipped Task #${curId}`, "warn");
    updateTaskStatus(curId, "done");
    setTasks(p => p.map(t => t.id === curId ? { ...t, status: "done" } : t));
  }, [curId, addLog]);

  useEffect(() => () => kill(), []);

  const fmt = (ms: number) => {
    const s = Math.floor(ms / 1000);
    return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
  };

  return { state, curId, log, elapsed: fmt(elapsed), play, pause, resume, stop, skip };
}

// ═══ STATUS HELPERS ═══
const statusConfig: Record<string, { label: string; color: string; bg: string }> = {
  done:    { label: "DONE",    color: "#22c55e", bg: "rgba(34,197,94,0.15)" },
  running: { label: "RUNNING", color: "#3b82f6", bg: "rgba(59,130,246,0.15)" },
  paused:  { label: "PAUSED",  color: "#eab308", bg: "rgba(234,179,8,0.15)" },
  pending: { label: "PENDING", color: "#737373", bg: "rgba(115,115,115,0.1)" },
  blocked: { label: "BLOCKED", color: "#ef4444", bg: "rgba(239,68,68,0.15)" },
};

// ═══ MAIN PAGE ═══
export default function MissionDetail() {
  const params = useParams();
  const missionId = params?.id;
  const [mission, setMission] = useState<Mission | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"tasks"|"dag"|"log">("tasks");

  const engine = useEngine(tasks, setTasks);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [engine.log]);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`/api/v1/missions/${missionId}`);
        if (res.ok) {
          const data = await res.json();
          setMission(data);
          setTasks(data.tasks || []);
        }
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    }
    if (missionId) load();
  }, [missionId]);

  if (loading) return <div className="min-h-screen bg-neutral-950 text-neutral-50 flex items-center justify-center">Loading mission...</div>;
  if (!mission) return <div className="min-h-screen bg-neutral-950 text-neutral-50 flex items-center justify-center">Mission not found</div>;

  const stats = {
    total: tasks.length,
    done: tasks.filter(t => t.status === "done").length,
    running: tasks.filter(t => t.status === "running").length,
  };
  const pct = stats.total > 0 ? Math.round(stats.done / stats.total * 100) : 0;

  const logColors: Record<string, string> = {
    info: "text-neutral-500", run: "text-blue-400", success: "text-green-400", warn: "text-yellow-400", error: "text-red-400"
  };

  const TABS = [
    { id: "tasks" as const, label: "Tasks", icon: <FileText className="w-4 h-4" /> },
    { id: "dag" as const,   label: "DAG",   icon: <Layers className="w-4 h-4" /> },
    { id: "log" as const,   label: "Log",   icon: <Terminal className="w-4 h-4" /> },
  ];

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 p-6 font-sans">
      {/* Header */}
      <header className="flex items-center justify-between mb-8 border-b border-neutral-800 pb-6">
        <div className="flex items-center gap-4">
          <Link href="/">
            <Button variant="ghost" size="icon" className="text-neutral-400 hover:text-white">
              <ChevronLeft className="h-6 w-6" />
            </Button>
          </Link>
          <div>
            <h1 className="text-xl font-bold tracking-tight">{mission.title}</h1>
            <p className="text-sm text-neutral-500 mt-1">{mission.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-mono text-neutral-600">m_{mission.id}</span>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-neutral-900 border border-neutral-800">
            <Clock className="w-3 h-3 text-neutral-500" />
            <span className="text-xs font-mono text-neutral-400">{engine.elapsed}</span>
          </div>
        </div>
      </header>

      {/* Engine Controls */}
      <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-4 mb-6">
        <div className="flex items-center gap-3 flex-wrap">
          {/* State badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-neutral-800 border border-neutral-700">
            <div className={`w-2 h-2 rounded-full ${engine.state === "running" ? "bg-blue-500 animate-pulse" : engine.state === "done" ? "bg-green-500" : "bg-neutral-500"}`} />
            <span className="text-[10px] font-mono text-neutral-400 uppercase">{engine.state === "idle" ? "READY" : engine.state.toUpperCase()}</span>
          </div>

          {/* Progress */}
          <div className="flex items-center gap-2">
            <div className="w-24 h-1.5 bg-neutral-800 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-blue-600 to-green-500 rounded-full transition-all duration-500" style={{ width: `${pct}%` }} />
            </div>
            <span className="text-xs font-mono text-neutral-500">{pct}%</span>
          </div>

          <div className="w-px h-6 bg-neutral-800" />

          {/* Controls */}
          {(engine.state === "idle" || engine.state === "done") && (
            <Button size="sm" onClick={engine.play} className="bg-green-600 hover:bg-green-700 gap-2" disabled={engine.state === "done"}>
              <Play className="w-3 h-3" /> Play
            </Button>
          )}
          {engine.state === "running" && (
            <Button size="sm" onClick={engine.pause} variant="outline" className="border-neutral-700 gap-2">
              <Pause className="w-3 h-3" /> Pause
            </Button>
          )}
          {engine.state === "paused" && (
            <Button size="sm" onClick={engine.resume} className="bg-green-600 hover:bg-green-700 gap-2">
              <Play className="w-3 h-3" /> Resume
            </Button>
          )}
          <Button size="sm" onClick={engine.skip} variant="ghost" disabled={!engine.curId} className="gap-2 text-neutral-400">
            <SkipForward className="w-3 h-3" /> Skip
          </Button>
          <Button size="sm" onClick={engine.stop} variant="ghost" disabled={engine.state === "idle"} className="gap-2 text-neutral-400">
            <Square className="w-3 h-3" /> Stop
          </Button>

          {/* Stats */}
          <div className="ml-auto flex gap-3">
            <div className="text-center">
              <div className="text-lg font-bold text-green-500">{stats.done}</div>
              <div className="text-[8px] font-mono text-neutral-600 uppercase">Done</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-blue-500">{stats.running}</div>
              <div className="text-[8px] font-mono text-neutral-600 uppercase">Active</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-neutral-500">{stats.total - stats.done - stats.running}</div>
              <div className="text-[8px] font-mono text-neutral-600 uppercase">Queue</div>
            </div>
          </div>
        </div>

        {engine.curId && (
          <div className="mt-3 flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-900/10 border border-blue-900/30">
            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
            <span className="text-[10px] font-mono text-neutral-500">EXECUTING</span>
            <span className="text-xs font-mono text-blue-400">Task #{engine.curId}</span>
            <span className="text-xs text-neutral-500 ml-2">{tasks.find(t => t.id === engine.curId)?.label}</span>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-neutral-900 rounded-xl p-1 border border-neutral-800">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all ${
              tab === t.id
                ? "bg-neutral-800 text-white shadow-sm"
                : "text-neutral-500 hover:text-neutral-300"
            }`}
          >
            {t.icon} {t.label}
            {t.id === "log" && engine.log.length > 0 && (
              <span className="text-[10px] bg-neutral-700 px-1.5 rounded-full">{engine.log.length}</span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === "tasks" && (
        <div className="space-y-2">
          {tasks.map((task, i) => {
            const sc = statusConfig[task.status] || statusConfig.pending;
            const isRunning = task.status === "running";
            return (
              <div
                key={task.id}
                className={`bg-neutral-900/50 border rounded-xl p-4 transition-all ${
                  isRunning ? "border-blue-800/50 shadow-[0_0_15px_rgba(59,130,246,0.1)]" : "border-neutral-800"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold ${
                    task.status === "done" ? "bg-green-900/20 text-green-500" :
                    isRunning ? "bg-blue-900/20 text-blue-400" : "bg-neutral-800 text-neutral-500"
                  }`}>
                    {task.status === "done" ? <CheckCircle2 className="w-4 h-4" /> : i + 1}
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-sm">{task.label}</div>
                    <div className="text-[10px] font-mono text-neutral-600 mt-0.5">
                      skill: {task.skill} • order: {task.order}
                    </div>
                  </div>
                  <span
                    className="text-[10px] font-mono px-2 py-1 rounded-full border"
                    style={{ color: sc.color, background: sc.bg, borderColor: `${sc.color}30` }}
                  >
                    {sc.label}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {tab === "dag" && (
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-6">
          <svg width="100%" height={Math.max(tasks.length * 70 + 80, 200)} viewBox={`0 0 700 ${Math.max(tasks.length * 70 + 80, 200)}`}>
            {/* Hub node */}
            <rect x="280" y="10" width="140" height="40" rx="12" fill="url(#hubGrad)" stroke="#818cf8" strokeWidth="2" />
            <text x="350" y="35" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">🛰️ NEXUS HUB</text>
            <defs>
              <linearGradient id="hubGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#1e40af" />
                <stop offset="100%" stopColor="#7c3aed" />
              </linearGradient>
            </defs>

            {tasks.map((task, i) => {
              const y = 80 + i * 70;
              const sc = statusConfig[task.status] || statusConfig.pending;
              const isRunning = task.status === "running";

              return (
                <g key={task.id}>
                  {/* Edge */}
                  <line x1="350" y1="50" x2="350" y2={y} stroke={sc.color} strokeWidth={isRunning ? 2 : 1} strokeDasharray={task.status === "pending" ? "4 3" : "none"} opacity={0.5} />
                  {isRunning && (
                    <circle r="3" fill={sc.color}>
                      <animateMotion dur="1s" repeatCount="indefinite" path={`M350,50 L350,${y}`} />
                    </circle>
                  )}

                  {/* Task node */}
                  {isRunning && (
                    <rect x="198" y={y - 2} width="304" height="44" rx="12" fill="none" stroke="#3b82f6" strokeWidth="1.5" opacity={0.3}>
                      <animate attributeName="opacity" values="0.3;0.1;0.3" dur="1.5s" repeatCount="indefinite" />
                    </rect>
                  )}
                  <rect x="200" y={y} width="300" height="40" rx="10" fill={sc.bg} stroke={`${sc.color}50`} strokeWidth="1" />

                  {/* Status dot */}
                  <circle cx="220" cy={y + 20} r="4" fill={sc.color} />
                  {isRunning && (
                    <circle cx="220" cy={y + 20} r="4" fill={sc.color}>
                      <animate attributeName="r" values="4;8;4" dur="1.2s" repeatCount="indefinite" />
                      <animate attributeName="opacity" values="0.5;0;0.5" dur="1.2s" repeatCount="indefinite" />
                    </circle>
                  )}

                  {/* Label */}
                  <text x="235" y={y + 17} fill="white" fontSize="11" fontWeight="600">{task.label}</text>
                  <text x="235" y={y + 32} fill="#737373" fontSize="9" fontFamily="monospace">{task.skill} • #{task.id}</text>

                  {/* Status label */}
                  <text x="480" y={y + 24} fill={sc.color} fontSize="9" fontFamily="monospace" textAnchor="end">{sc.label}</text>
                </g>
              );
            })}
          </svg>
        </div>
      )}

      {tab === "log" && (
        <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-neutral-800 flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500" />
            <div className="w-2.5 h-2.5 rounded-full bg-yellow-500" />
            <div className="w-2.5 h-2.5 rounded-full bg-green-500" />
            <span className="text-[10px] font-mono text-neutral-600 ml-3">AGENT OS — PIPELINE LOG</span>
            <span className="text-[10px] font-mono text-neutral-700 ml-auto">{engine.log.length} events</span>
          </div>
          <div ref={logRef} className="h-64 overflow-y-auto p-4 space-y-1">
            {engine.log.length === 0 ? (
              <span className="text-xs font-mono text-neutral-700">Awaiting engine start…</span>
            ) : engine.log.map(e => (
              <div key={e.id} className="flex gap-4">
                <span className="text-[10px] font-mono text-neutral-700 flex-shrink-0">{e.ts}</span>
                <span className={`text-xs font-mono ${logColors[e.type] || "text-neutral-500"}`}>{e.msg}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <footer className="mt-12 text-center text-neutral-700 text-[10px] font-mono border-t border-neutral-900 pt-8">
        NEXUS MISSION ENGINE v2.0 • NÜMTÉMA PROPRIETARY • RRLA-NATIVE
      </footer>
    </div>
  );
}
