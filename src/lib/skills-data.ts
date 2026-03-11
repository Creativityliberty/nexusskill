export interface SkillFile {
  name: string;
  type: "file" | "dir";
  children?: SkillFile[];
}

export interface SkillData {
  name: string;
  description: string;
  files: SkillFile[];
}

export const SKILLS_CATALOG: SkillData[] = [
  {
    name: "agent-pocketflow",
    description: "Build autonomous AI agents using the PocketFlow framework with custom nodes, flows, and LLM routing.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "agent.yaml", type: "file" },
      { name: "scripts", type: "dir", children: [
        { name: "agent.py", type: "file" },
        { name: "flow.py", type: "file" },
        { name: "llm_client.py", type: "file" },
        { name: "prompts.py", type: "file" },
        { name: "nodes", type: "dir", children: [
          { name: "base_node.py", type: "file" },
          { name: "doc_nodes.py", type: "file" },
          { name: "git_nodes.py", type: "file" },
          { name: "llm_node.py", type: "file" },
        ]},
      ]},
      { name: "examples", type: "dir", children: [
        { name: "create_custom_agent.py", type: "file" },
      ]},
    ]
  },
  {
    name: "artifact-maker",
    description: "Multi-format output engine for AI agents. Converts agent results into real artifacts - Markdown, JSON, PDF reports, charts/images, audio (TTS), video slideshows, and code files.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "scripts", type: "dir", children: [
        { name: "artifact_engine.py", type: "file" },
        { name: "renderers", type: "dir", children: [
          { name: "chart_renderer.py", type: "file" },
          { name: "pdf_renderer.py", type: "file" },
          { name: "audio_renderer.py", type: "file" },
          { name: "video_renderer.py", type: "file" },
        ]},
      ]},
      { name: "templates", type: "dir", children: [
        { name: "report.html", type: "file" },
      ]},
      { name: "examples", type: "dir", children: [
        { name: "demo_artifacts.py", type: "file" },
      ]},
    ]
  },
  {
    name: "artifacts-maker",
    description: "Collect, name, organize and track all output artifacts produced during a workflow or task execution. Creates a structured artifacts/ directory with a manifest.json index.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "references", type: "dir", children: [{ name: "artifact-types.md", type: "file" }] },
      { name: "scripts", type: "dir", children: [{ name: "artifact_registry.py", type: "file" }] },
    ]
  },
  {
    name: "blueprint-maker",
    description: "Universal domain-agnostic blueprint generator. Creates structured project blueprints for ANY field - business, product, research, education, engineering, or custom.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "test_blueprint.md", type: "file" },
      { name: "scripts", type: "dir", children: [{ name: "blueprint_engine.py", type: "file" }] },
    ]
  },
  {
    name: "commit",
    description: "Create well-formatted git commits. Use when the user wants to commit changes, stage files, or run a git commit workflow.",
    files: [{ name: "SKILL.md", type: "file" }]
  },
  {
    name: "dag-taskview",
    description: "Visual DAG task tree system for project decomposition and tracking. Generates Mermaid diagrams showing task dependencies, progress, and critical paths.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "scripts", type: "dir", children: [
        { name: "dag_engine.py", type: "file" },
        { name: "progress_tracker.py", type: "file" },
      ]},
      { name: "examples", type: "dir", children: [{ name: "sample_dag.py", type: "file" }] },
      { name: "templates", type: "dir", children: [{ name: "task_template.yaml", type: "file" }] },
    ]
  },
  {
    name: "flow-orchestrator",
    description: "Advanced multi-agent workflow orchestration engine built on PocketFlow. Use for complex multi-agent pipelines with pause/resume, state snapshots, and coordinated agent pools.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "scripts", type: "dir", children: [{ name: "orchestrator.py", type: "file" }] },
      { name: "examples", type: "dir", children: [{ name: "quick_start.py", type: "file" }] },
      { name: "templates", type: "dir", children: [{ name: "multi_agent_pipeline.py", type: "file" }] },
    ]
  },
  {
    name: "kernel-forge",
    description: "Build a complete WMAG Kernel (World Model + Action Graph) - a production-grade multi-agent orchestration system with multi-tenant Action Registry, LLM Planner, and Policy Gate.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "assets", type: "dir", children: [{ name: "registry.yaml.template", type: "file" }] },
      { name: "examples", type: "dir", children: [{ name: "support-kernel.md", type: "file" }] },
      { name: "references", type: "dir", children: [
        { name: "kernel-ports.md", type: "file" },
        { name: "policy-gate.md", type: "file" },
        { name: "sse-streaming.md", type: "file" },
      ]},
    ]
  },
  {
    name: "keybindings-help",
    description: "Customize keyboard shortcuts, rebind keys, add chord bindings, or modify keybindings configuration for Claude Code.",
    files: [{ name: "SKILL.md", type: "file" }]
  },
  {
    name: "mcp-builder",
    description: "Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "LICENSE.txt", type: "file" },
      { name: "reference", type: "dir", children: [
        { name: "mcp_best_practices.md", type: "file" },
        { name: "node_mcp_server.md", type: "file" },
        { name: "python_mcp_server.md", type: "file" },
        { name: "evaluation.md", type: "file" },
      ]},
      { name: "scripts", type: "dir", children: [
        { name: "connections.py", type: "file" },
        { name: "evaluation.py", type: "file" },
      ]},
    ]
  },
  {
    name: "morsel-tasks",
    description: "Execute tasks as atomic 'morsels' - the smallest indivisible unit of work. Handles checkpointing, lock files, exponential backoff retry, and self-correction.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "references", type: "dir", children: [{ name: "morsel-patterns.md", type: "file" }] },
      { name: "scripts", type: "dir", children: [{ name: "morsel_runner.py", type: "file" }] },
    ]
  },
  {
    name: "nanoclaw-forge",
    description: "Build and deploy NanoClaw agents - secure, lightweight autonomous AI agents in containerized environments with Docker-based architecture and isolated IPC.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "examples", type: "dir", children: [{ name: "full_pipeline.md", type: "file" }] },
      { name: "scripts", type: "dir", children: [{ name: "forge_bridge.py", type: "file" }] },
    ]
  },
  {
    name: "num-agents",
    description: "Build, scaffold, and design AI agent systems using the Nüm Agents SDK - a universe-based orchestration framework with YAML specs and execution hooks.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "assets", type: "dir", children: [{ name: "example-agent.yaml", type: "file" }] },
      { name: "references", type: "dir", children: [
        { name: "agent-spec-schema.md", type: "file" },
        { name: "flow-patterns.md", type: "file" },
        { name: "universe-catalog.md", type: "file" },
      ]},
      { name: "scripts", type: "dir", children: [{ name: "scaffold_agent.py", type: "file" }] },
    ]
  },
  {
    name: "orchestra-forge",
    description: "Full-stack AI agent builder combining Nüm Agents architecture, PocketFlow execution engine, and Skill Architect quality pipeline.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "examples", type: "dir", children: [{ name: "pdf-summarizer.md", type: "file" }] },
    ]
  },
  {
    name: "pocketflow",
    description: "Build LLM-powered workflows using the PocketFlow framework - a minimalist Python library for chaining AI nodes into graphs and pipelines.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "scripts", type: "dir", children: [{ name: "pocketflow.py", type: "file" }] },
    ]
  },
  {
    name: "review-pr",
    description: "Review a GitHub Pull Request - analyze code changes, spot bugs, check style, assess tests, and write a structured review comment.",
    files: [{ name: "SKILL.md", type: "file" }]
  },
  {
    name: "session-start-hook",
    description: "Create and develop startup hooks for Claude Code on the web. Set up a repository for Claude Code with SessionStart hooks for tests and linters.",
    files: [{ name: "SKILL.md", type: "file" }]
  },
  {
    name: "skill-architect",
    description: "Multi-agent pipeline that analyzes, refactors, reviews, audits, and documents an existing Claude Code skill.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "examples", type: "dir", children: [
        { name: "commit-skill-pipeline.md", type: "file" },
        { name: "ui-style-generator-pipeline.md", type: "file" },
      ]},
      { name: "references", type: "dir", children: [{ name: "agent-roles.md", type: "file" }] },
      { name: "scripts", type: "dir", children: [{ name: "skill_pipeline.py", type: "file" }] },
    ]
  },
  {
    name: "skill-creator",
    description: "Guide for creating effective Claude Code skills. Use when the user wants to create a new skill, update an existing skill, or learn how to structure a skill.",
    files: [{ name: "SKILL.md", type: "file" }]
  },
  {
    name: "skill-ide-setup",
    description: "Automatically configures the project for AI-powered IDEs (Cursor, Windsurf, Trae, Cline, Roo Code).",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "scripts", type: "dir", children: [{ name: "setup.py", type: "file" }] },
      { name: "templates", type: "dir", children: [{ name: "base_rules.md", type: "file" }] },
    ]
  },
  {
    name: "task-tree",
    description: "Decompose a complex goal into a hierarchical DAG of tasks. Each task maps to a skill, has explicit dependencies, and declares its expected output artifact.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "references", type: "dir", children: [{ name: "decomposition-strategies.md", type: "file" }] },
      { name: "scripts", type: "dir", children: [{ name: "task_tree.py", type: "file" }] },
    ]
  },
  {
    name: "ui-style-generator",
    description: "Generate a complete UI Design System and Styleguide. Produces color tokens, typography, spacing, animations, layout, shadows, gradients, and full CSS variables export.",
    files: [
      { name: "SKILL.md", type: "file" },
      { name: "references", type: "dir", children: [
        { name: "design-system-schema.md", type: "file" },
        { name: "markdown-template.md", type: "file" },
      ]},
      { name: "scripts", type: "dir", children: [{ name: "generate_markdown.ts", type: "file" }] },
    ]
  },
];
