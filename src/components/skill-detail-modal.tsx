"use client"

import { X, FolderOpen, FileText, ChevronRight, ChevronDown, Code, Terminal } from "lucide-react";
import { useState } from "react";
import type { SkillData, SkillFile } from "@/lib/skills-data";

function FileTreeNode({ node, depth = 0 }: { node: SkillFile; depth?: number }) {
  const [open, setOpen] = useState(depth < 2);
  const isDir = node.type === "dir";

  return (
    <div>
      <div
        className={`flex items-center gap-2 py-1 px-2 rounded cursor-pointer transition-colors ${
          isDir ? "hover:bg-neutral-800/60 text-neutral-300" : "hover:bg-neutral-800/40 text-neutral-400"
        }`}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
        onClick={() => isDir && setOpen(!open)}
      >
        {isDir ? (
          <>
            {open ? <ChevronDown className="w-3 h-3 text-blue-500" /> : <ChevronRight className="w-3 h-3 text-neutral-500" />}
            <FolderOpen className="w-4 h-4 text-blue-400" />
          </>
        ) : (
          <>
            <span className="w-3" />
            <FileText className="w-4 h-4 text-neutral-500" />
          </>
        )}
        <span className={`text-sm font-mono ${isDir ? "font-semibold text-blue-300" : ""}`}>
          {node.name}
        </span>
        {node.name.endsWith(".py") && <Code className="w-3 h-3 text-yellow-500/50 ml-auto" />}
        {node.name.endsWith(".ts") && <Code className="w-3 h-3 text-blue-500/50 ml-auto" />}
        {node.name.endsWith(".md") && <FileText className="w-3 h-3 text-green-500/50 ml-auto" />}
      </div>
      {isDir && open && node.children?.map((child, i) => (
        <FileTreeNode key={i} node={child} depth={depth + 1} />
      ))}
    </div>
  );
}

export default function SkillDetailModal({
  skill,
  onClose,
}: {
  skill: SkillData;
  onClose: () => void;
}) {
  const fileCount = countFiles(skill.files);
  const dirCount = countDirs(skill.files);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      {/* Modal */}
      <div
        className="relative w-full max-w-2xl max-h-[85vh] bg-neutral-900/95 border border-neutral-700/50 rounded-xl shadow-2xl shadow-blue-950/20 overflow-hidden animate-in fade-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-neutral-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
              <Terminal className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">{skill.name}</h2>
              <div className="flex gap-3 mt-1">
                <span className="text-[10px] font-mono text-neutral-500">{fileCount} files</span>
                <span className="text-[10px] font-mono text-neutral-500">{dirCount} dirs</span>
                <span className="text-[10px] font-mono text-green-600">v1.0.0</span>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-neutral-800 text-neutral-500 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(85vh-180px)]">
          {/* Description */}
          <div className="p-6 border-b border-neutral-800/50">
            <h3 className="text-xs font-mono text-neutral-500 uppercase tracking-widest mb-2">Description</h3>
            <p className="text-sm text-neutral-300 leading-relaxed">{skill.description}</p>
          </div>

          {/* Tags */}
          <div className="px-6 py-4 border-b border-neutral-800/50 flex gap-2 flex-wrap">
            <span className="px-2 py-0.5 bg-green-900/20 text-green-500 text-[10px] rounded border border-green-800/30">
              Proprietary
            </span>
            <span className="px-2 py-0.5 bg-blue-900/20 text-blue-400 text-[10px] rounded border border-blue-800/30">
              L3 Agent Compatible
            </span>
            <span className="px-2 py-0.5 bg-purple-900/20 text-purple-400 text-[10px] rounded border border-purple-800/30">
              Nümtéma Certified
            </span>
          </div>

          {/* File Tree */}
          <div className="p-6">
            <h3 className="text-xs font-mono text-neutral-500 uppercase tracking-widest mb-3">
              Skill Architecture
            </h3>
            <div className="bg-neutral-950 border border-neutral-800 rounded-lg p-3">
              <div className="flex items-center gap-2 pb-2 mb-2 border-b border-neutral-800/50">
                <FolderOpen className="w-4 h-4 text-yellow-500" />
                <span className="text-sm font-mono font-bold text-yellow-400">{skill.name}/</span>
              </div>
              {skill.files.map((file, i) => (
                <FileTreeNode key={i} node={file} depth={0} />
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-neutral-800 bg-neutral-950/50 flex justify-between items-center">
          <span className="text-[10px] font-mono text-neutral-600">
            NÜMTÉMA SKILL REGISTRY • MESH ID: {skill.name.slice(0, 8).toUpperCase()}
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-sm rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function countFiles(files: SkillFile[]): number {
  return files.reduce((acc, f) => {
    if (f.type === "file") return acc + 1;
    return acc + (f.children ? countFiles(f.children) : 0);
  }, 0);
}

function countDirs(files: SkillFile[]): number {
  return files.reduce((acc, f) => {
    if (f.type === "dir") return acc + 1 + (f.children ? countDirs(f.children) : 0);
    return acc;
  }, 0);
}
