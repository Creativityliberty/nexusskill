#!/usr/bin/env python3
"""
nexus-skill.py — Modern CLI for managing AI agent skills.
Supports local portfolios (aiskills-repo) and multi-agent installation.

Usage:
    python nexus-skill.py ls
    python nexus-skill.py info <name>
    python nexus-skill.py install <name> [--agents all]
    python nexus-skill.py sync
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Dict

# --- Configuration ---
SKILLS_DIR = Path(".agents/skills")
LOCAL_PORTFOLIO = Path("aiskills-repo/skills")
ALT_LOCAL_PORTFOLIO = Path("../aiskills-repo/skills")

# --- UI Helpers ---
class Colors:
    CYAN = '\033[0;36m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    BOLD = '\033[1m'
    NC = '\033[0m'

def log_info(msg): print(f"{Colors.BLUE}ℹ{Colors.NC} {msg}", file=sys.stderr)
def log_success(msg): print(f"{Colors.GREEN}✓{Colors.NC} {msg}", file=sys.stderr)
def log_warn(msg): print(f"{Colors.YELLOW}⚠{Colors.NC} {msg}", file=sys.stderr)
def log_error(msg): print(f"{Colors.RED}✗{Colors.NC} {msg}", file=sys.stderr)

# --- Agent Profiles ---
SCOPED_AGENTS = {
    "claude": ".claude/skills",
    "cursor": ".cursor/skills",
    "windsurf": ".windsurf/skills",
    "cline": ".cline/skills",
    "roo": ".roo/skills",
    "continue": ".continue/skills",
    "trae": ".trae/skills",
    "antigravity": ".agent/skills",
}

AGENT_DETECTION = {
    "claude": Path.home() / ".claude",
    "cursor": Path.home() / ".cursor",
    "windsurf": Path.home() / ".codeium/windsurf",
    "cline": Path.home() / ".cline",
    "roo": Path.home() / ".roo",
    "continue": Path.home() / ".continue",
    "trae": Path.home() / ".trae",
}

# --- Core Logic ---

def get_local_portfolio_path() -> Optional[Path]:
    """Find the local aiskills portfolio."""
    if LOCAL_PORTFOLIO.exists() and LOCAL_PORTFOLIO.is_dir():
        return LOCAL_PORTFOLIO
    if ALT_LOCAL_PORTFOLIO.exists() and ALT_LOCAL_PORTFOLIO.is_dir():
        return ALT_LOCAL_PORTFOLIO
    return None

def detect_agents() -> List[str]:
    """Detect which AI agents are installed on the system."""
    detected = []
    for agent, path in AGENT_DETECTION.items():
        if path.exists() and path.is_dir():
            detected.append(agent)
    return detected

def list_skills():
    """List available skills from local portfolio."""
    portfolio = get_local_portfolio_path()
    if not portfolio:
        log_warn("Local aiskills-repo not found. Only online registry would be available.")
        return

    print(f"\n{Colors.BOLD}{Colors.CYAN}--- Available Skills (Local Portfolio) ---{Colors.NC}\n")
    skills = sorted([d.name for d in portfolio.iterdir() if d.is_dir()])
    
    for skill in skills:
        skill_file = portfolio / skill / "SKILL.md"
        desc = ""
        if skill_file.exists():
            content = skill_file.read_text(encoding='utf-8', errors='replace')
            match = re.search(r'description:\s*>\s*(.*?)(?=\n\w+:|---)', content, re.DOTALL)
            if not match:
                match = re.search(r'description:\s*(.*?)\n', content)
            
            if match:
                desc = match.group(1).strip().replace('\n', ' ')
                if len(desc) > 80: desc = desc[:77] + "..."

        print(f"  {Colors.GREEN}{skill:<20}{Colors.NC} {desc}")
    print()

def show_info(name: str):
    """Show detailed info for a skill."""
    portfolio = get_local_portfolio_path()
    if not portfolio:
        log_error("Portfolio not found.")
        return

    skill_path = portfolio / name
    if not skill_path.exists():
        log_error(f"Skill '{name}' not found in local portfolio.")
        return

    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        log_error(f"SKILL.md missing for '{name}'.")
        return

    content = skill_file.read_text(encoding='utf-8', errors='replace')
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}Skill: {name}{Colors.NC}")
    print("=" * (len(name) + 7))
    
    # Simple extraction of frontmatter or title
    lines = content.split('\n')
    in_description = False
    description = []
    
    for line in lines:
        if line.startswith('description:'):
            in_description = True
            if '>' not in line:
                description.append(line.replace('description:', '').strip())
                in_description = False
            continue
        if in_description:
            if line.startswith('  ') or line.strip() == '':
                description.append(line.strip())
            else:
                in_description = False
        
        if line.startswith('# '):
            print(f"\n{Colors.BOLD}Title:{Colors.NC} {line[2:]}")

    if description:
        print(f"\n{Colors.BOLD}Description & Triggers:{Colors.NC}")
        print(" " + " ".join(description))

    # Look for Example usage
    if '## Example' in content or '## Usage' in content:
        print(f"\n{Colors.BOLD}Usage Highlights:{Colors.NC}")
        for line in lines:
            if line.startswith('## '):
                if any(k in line.lower() for k in ['example', 'usage', 'how to']):
                    print(f"  - {line[3:]}")

    print(f"\n{Colors.BLUE}Path:{Colors.NC} {skill_file}\n")

def install_skill(name: str, agents: List[str] = None):
    """Install a skill and create symlinks for agents."""
    portfolio = get_local_portfolio_path()
    if not portfolio:
        log_error("Portfolio not found.")
        return

    src_file = portfolio / name / "SKILL.md"
    if not src_file.exists():
        log_error(f"Skill '{name}' not found.")
        return

    # 1. Install to project core
    dest_dir = SKILLS_DIR / name
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / "SKILL.md"
    shutil.copy2(src_file, dest_file)
    log_success(f"Installed {name} to {dest_file}")

    # 2. Symlink to agents
    if agents == ['all']:
        agents = detect_agents()
    elif not agents:
        agents = []

    for agent in agents:
        if agent in SCOPED_AGENTS:
            agent_dir = Path(SCOPED_AGENTS[agent]) / name
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            # Simple copy for Windows/compatibility, or symlink if possible
            agent_file = agent_dir / "SKILL.md"
            shutil.copy2(dest_file, agent_file)
            log_success(f"Linked {name} for {agent} ({agent_file})")

def main():
    parser = argparse.ArgumentParser(description="Nexus Skill CLI — Manage AI agent skills")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # ls / list
    subparsers.add_parser("ls", help="List available skills")
    subparsers.add_parser("list", help="List available skills")

    # info
    info_parser = subparsers.add_parser("info", help="Show skill details")
    info_parser.add_argument("name", help="Name of the skill")

    # install
    install_parser = subparsers.add_parser("install", help="Install a skill")
    install_parser.add_argument("name", help="Name of the skill")
    install_parser.add_argument("--agents", help="Comma-separated agents or 'all'", default="")

    # sync
    subparsers.add_parser("sync", help="Sync all project skills to detected agents")

    args = parser.parse_args()

    if args.command in ["ls", "list"]:
        list_skills()
    elif args.command == "info":
        show_info(args.name)
    elif args.command == "install":
        agents = args.agents.split(',') if args.agents else []
        install_skill(args.name, agents)
    elif args.command == "sync":
        log_info("Syncing all project skills...")
        if not SKILLS_DIR.exists():
            log_warn("No project skills found to sync.")
            return
        
        agents = detect_agents()
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir():
                install_skill(skill_dir.name, agents)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
