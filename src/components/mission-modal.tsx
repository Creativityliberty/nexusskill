"use client"

import { X, Rocket, Zap, Target } from "lucide-react";
import { useState } from "react";

interface MissionModalProps {
  onClose: () => void;
  onSubmit: (data: { goal: string; priority: string; agent: string }) => void;
}

export default function MissionModal({ onClose, onSubmit }: MissionModalProps) {
  const [goal, setGoal] = useState("");
  const [priority, setPriority] = useState("normal");
  const [agent, setAgent] = useState("claude-sonnet");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!goal.trim()) return;
    setSubmitting(true);
    await onSubmit({ goal, priority, agent });
    setSubmitting(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      <div
        className="relative w-full max-w-lg bg-neutral-900/95 border border-neutral-700/50 rounded-xl shadow-2xl shadow-blue-950/20 overflow-hidden animate-in fade-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-neutral-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-green-600 to-emerald-800 rounded-lg flex items-center justify-center">
              <Rocket className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">New Mission</h2>
              <p className="text-xs text-neutral-500">Define your orchestration objective</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-neutral-800 text-neutral-500 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <div className="p-6 space-y-5">
          {/* Objective */}
          <div>
            <label className="text-xs font-mono text-neutral-500 uppercase tracking-widest mb-2 block">
              <Target className="w-3 h-3 inline mr-1" /> Mission Objective
            </label>
            <textarea
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="e.g., Build a SaaS dashboard with authentication, Stripe integration, and real-time analytics..."
              className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-3 text-sm text-neutral-200 placeholder:text-neutral-600 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none h-24"
            />
          </div>

          {/* Priority + Agent Row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-mono text-neutral-500 uppercase tracking-widest mb-2 block">
                <Zap className="w-3 h-3 inline mr-1" /> Priority
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2.5 text-sm text-neutral-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="low">🟢 Low</option>
                <option value="normal">🟡 Normal</option>
                <option value="high">🔴 High</option>
                <option value="critical">⚡ Critical</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-mono text-neutral-500 uppercase tracking-widest mb-2 block">
                Agent Focus
              </label>
              <select
                value={agent}
                onChange={(e) => setAgent(e.target.value)}
                className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2.5 text-sm text-neutral-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="antigravity">Antigravity (Local Elite)</option>
                <option value="claude-sonnet">Claude 3.7 Sonnet</option>
                <option value="claude-opus">Claude 3.5 Opus</option>
                <option value="gemini-flash">Gemini 2.0 Flash</option>
                <option value="deepseek-r1">DeepSeek R1</option>
                <option value="cursor-agent">Cursor Agent</option>
                <option value="windsurf-agent">Windsurf Agent</option>
              </select>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-neutral-800 bg-neutral-950/50 flex justify-between items-center">
          <span className="text-[10px] font-mono text-neutral-600">
            NEXUS MISSION ENGINE v2.0
          </span>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm text-neutral-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={!goal.trim() || submitting}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              {submitting ? (
                <>
                  <Rocket className="w-4 h-4 animate-bounce" /> Launching...
                </>
              ) : (
                <>
                  <Rocket className="w-4 h-4" /> Launch Mission
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
