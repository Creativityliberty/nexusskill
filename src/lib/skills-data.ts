export interface SkillData {
  name: string;
  description: string;
}

export const SKILLS_CATALOG: SkillData[] = [
  {
    name: "agent-pocketflow",
    description: "Build autonomous AI agents using the PocketFlow framework with custom nodes, flows, and LLM routing."
  },
  {
    name: "artifact-maker",
    description: "Multi-format output engine for AI agents. Converts agent results into real artifacts - Markdown, JSON, PDF reports, charts/images, audio (TTS), video slideshows, and code files."
  },
  {
    name: "artifacts-maker",
    description: "Collect, name, organize and track all output artifacts produced during a workflow or task execution. Creates a structured artifacts/ directory with a manifest.json index."
  },
  {
    name: "blueprint-maker",
    description: "Universal domain-agnostic blueprint generator. Creates structured project blueprints for ANY field - business, product, research, education, engineering, or custom."
  },
  {
    name: "commit",
    description: "Create well-formatted git commits. Use when the user wants to commit changes, stage files, or run a git commit workflow."
  },
  {
    name: "dag-taskview",
    description: "Visual DAG (Directed Acyclic Graph) task tree system for project decomposition and tracking. Generates Mermaid diagrams showing task dependencies, progress, and critical paths."
  },
  {
    name: "flow-orchestrator",
    description: "Advanced multi-agent workflow orchestration engine built on PocketFlow. Use for complex multi-agent pipelines with pause/resume, state snapshots, and coordinated agent pools."
  },
  {
    name: "kernel-forge",
    description: "Build a complete WMAG Kernel (World Model + Action Graph) - a production-grade multi-agent orchestration system with multi-tenant Action Registry, LLM Planner, and Policy Gate."
  },
  {
    name: "keybindings-help",
    description: "Customize keyboard shortcuts, rebind keys, add chord bindings, or modify keybindings configuration for Claude Code."
  },
  {
    name: "mcp-builder",
    description: "Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools."
  },
  {
    name: "morsel-tasks",
    description: "Execute tasks as atomic 'morsels' - the smallest indivisible unit of work. Handles checkpointing, lock files, exponential backoff retry, and self-correction."
  },
  {
    name: "nanoclaw-forge",
    description: "Build and deploy NanoClaw agents - secure, lightweight autonomous AI agents in containerized environments with Docker-based architecture and isolated IPC."
  },
  {
    name: "num-agents",
    description: "Build, scaffold, and design AI agent systems using the Nüm Agents SDK - a universe-based orchestration framework with YAML specs and execution hooks."
  },
  {
    name: "orchestra-forge",
    description: "Full-stack AI agent builder combining Nüm Agents architecture, PocketFlow execution engine, and Skill Architect quality pipeline. Design, build, and validate complete AI agents."
  },
  {
    name: "pocketflow",
    description: "Build LLM-powered workflows using the PocketFlow framework - a minimalist Python library for chaining AI nodes into graphs and pipelines."
  },
  {
    name: "review-pr",
    description: "Review a GitHub Pull Request - analyze code changes, spot bugs, check style, assess tests, and write a structured review comment."
  },
  {
    name: "session-start-hook",
    description: "Create and develop startup hooks for Claude Code on the web. Set up a repository for Claude Code with SessionStart hooks for tests and linters."
  },
  {
    name: "skill-architect",
    description: "Multi-agent pipeline that analyzes, refactors, reviews, audits, and documents an existing Claude Code skill. Improve, audit, and optimize skill structure."
  },
  {
    name: "skill-creator",
    description: "Guide for creating effective Claude Code skills. Use when the user wants to create a new skill, update an existing skill, or learn how to structure a skill."
  },
  {
    name: "skill-ide-setup",
    description: "Automatically configures the project for AI-powered IDEs (Cursor, Windsurf, Trae, Cline, Roo Code). Optimize project setup for specific editors."
  },
  {
    name: "task-tree",
    description: "Decompose a complex goal into a hierarchical DAG of tasks. Each task maps to a skill, has explicit dependencies, and declares its expected output artifact."
  },
  {
    name: "ui-style-generator",
    description: "Generate a complete UI Design System and Styleguide. Produces color tokens, typography, spacing, animations, layout, shadows, gradients, and full CSS variables export."
  }
];
