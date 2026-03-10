#!/usr/bin/env bash
# install_skills.sh — Universal llms.txt skill installer
# Works standalone (no npm required) or alongside llmstxt-cli
#
# Usage:
#   bash install_skills.sh [options]
#
# Options:
#   --detect          Auto-detect dependencies and install matching skills
#   --install <name>  Install a specific skill by name/slug
#   --agents <list>   Comma-separated agent list, or "all" (default: auto-detect)
#   --full            Prefer llms-full.txt when available
#   --dry-run         Show what would be installed without writing files
#   --help            Show this help message

set -euo pipefail

# === Configuration ===
REGISTRY_BASE="https://llmstxthub.com"
SKILLS_DIR=".agents/skills"
VERSION="1.0.0"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# === Agent definitions ===
declare -A UNIVERSAL_AGENTS=(
  ["amp"]=".agents/skills"
  ["codex"]=".agents/skills"
  ["gemini-cli"]=".agents/skills"
  ["github-copilot"]=".agents/skills"
  ["kimi-code-cli"]=".agents/skills"
  ["opencode"]=".agents/skills"
)

declare -A SCOPED_AGENTS=(
  ["claude-code"]=".claude/skills"
  ["cursor"]=".cursor/skills"
  ["windsurf"]=".windsurf/skills"
  ["cline"]=".cline/skills"
  ["roo-code"]=".roo/skills"
  ["continue"]=".continue/skills"
  ["augment"]=".augment/skills"
  ["goose"]=".goose/skills"
  ["kilo-code"]=".kilocode/skills"
  ["trae"]=".trae/skills"
  ["junie"]=".junie/skills"
  ["qoder"]=".qoder/skills"
  ["qwen-code"]=".qwen/skills"
  ["openhands"]=".openhands/skills"
  ["kode"]=".kode/skills"
  ["kiro"]=".kiro/skills"
  ["mcpjam"]=".mcpjam/skills"
  ["mistral-vibe"]=".vibe/skills"
  ["droid"]=".factory/skills"
  ["antigravity"]=".agent/skills"
  ["codebuddy"]=".codebuddy/skills"
  ["command-code"]=".commandcode/skills"
  ["crush"]=".crush/skills"
  ["iflow"]=".iflow/skills"
  ["mux"]=".mux/skills"
  ["neovate"]=".neovate/skills"
  ["openclaw"]="skills"
  ["pi"]=".pi/skills"
  ["pochi"]=".pochi/skills"
  ["zencoder"]=".zencoder/skills"
  ["adal"]=".adal/skills"
)

# === Detection paths ===
declare -A AGENT_DETECTION=(
  ["claude-code"]="$HOME/.claude"
  ["cursor"]="$HOME/.cursor"
  ["windsurf"]="$HOME/.codeium/windsurf"
  ["cline"]="$HOME/.cline"
  ["roo-code"]="$HOME/.roo"
  ["continue"]="$HOME/.continue"
  ["augment"]="$HOME/.augment"
  ["goose"]="$HOME/.config/goose"
  ["amp"]="$HOME/.config/amp"
  ["codex"]="$HOME/.codex"
  ["opencode"]="$HOME/.config/opencode"
  ["kilo-code"]="$HOME/.kilocode"
  ["trae"]="$HOME/.trae"
  ["junie"]="$HOME/.junie"
  ["crush"]="$HOME/.config/crush"
  ["gemini-cli"]="$HOME/.config/gemini"
)

# === Functions ===

print_header() {
  echo -e "${CYAN}"
  echo "╔══════════════════════════════════════════╗"
  echo "║   llmstxt Skill Installer v${VERSION}       ║"
  echo "║   Universal AI Agent Skills Manager      ║"
  echo "╚══════════════════════════════════════════╝"
  echo -e "${NC}"
}

log_info() { echo -e "${BLUE}ℹ${NC} $1" >&2; }
log_success() { echo -e "${GREEN}✓${NC} $1" >&2; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1" >&2; }
log_error() { echo -e "${RED}✗${NC} $1" >&2; }

detect_agents() {
  local detected=()
  
  for agent in "${!AGENT_DETECTION[@]}"; do
    local path="${AGENT_DETECTION[$agent]}"
    if [ -d "$path" ]; then
      detected+=("$agent")
    fi
  done
  
  # Codex special case
  if [ -d "$HOME/.codex" ] || [ -d "/etc/codex" ]; then
    detected+=("codex")
  fi
  
  echo "${detected[@]}"
}

detect_dependencies() {
  local deps=()
  
  # Node.js
  if [ -f "package.json" ]; then
    log_info "Found package.json — scanning Node.js dependencies..."
    local node_deps
    local py_cmd="python3"
    if ! command -v python3 &>/dev/null; then py_cmd="python"; fi
    
    node_deps=$($py_cmd -c "
import json, sys
try:
    with open('package.json') as f:
        pkg = json.load(f)
    all_deps = list(pkg.get('dependencies', {}).keys()) + list(pkg.get('devDependencies', {}).keys())
    print(' '.join(all_deps))
except:
    pass
" 2>/dev/null || echo "")
    for dep in $node_deps; do
      deps+=("$dep")
    done
  fi
  
  # Python
  if [ -f "requirements.txt" ]; then
    log_info "Found requirements.txt — scanning Python dependencies..."
    while IFS= read -r line; do
      local pkg_name
      pkg_name=$(echo "$line" | sed 's/[>=<~!].*//' | sed 's/\[.*//' | tr -d '[:space:]')
      [ -n "$pkg_name" ] && [ "${pkg_name:0:1}" != "#" ] && deps+=("$pkg_name")
    done < requirements.txt
  fi
  
  if [ -f "pyproject.toml" ]; then
    log_info "Found pyproject.toml — scanning Python dependencies..."
    # Basic extraction — works for most cases
    local py_deps
    py_deps=$(python3 -c "
import re
with open('pyproject.toml') as f:
    content = f.read()
matches = re.findall(r'\"([a-zA-Z0-9_-]+)', content)
for m in matches:
    if len(m) > 2:
        print(m)
" 2>/dev/null || echo "")
    for dep in $py_deps; do
      deps+=("$dep")
    done
  fi
  
  # Rust
  if [ -f "Cargo.toml" ]; then
    log_info "Found Cargo.toml — scanning Rust dependencies..."
    local rust_deps
    rust_deps=$(grep -E '^\w+\s*=' Cargo.toml | grep -v '^\[' | awk -F'=' '{print $1}' | tr -d '[:space:]')
    for dep in $rust_deps; do
      deps+=("$dep")
    done
  fi
  
  # Go
  if [ -f "go.mod" ]; then
    log_info "Found go.mod — scanning Go dependencies..."
    local go_deps
    go_deps=$(grep -E '^\t' go.mod 2>/dev/null | awk '{print $1}' | xargs -I{} basename {} || echo "")
    for dep in $go_deps; do
      deps+=("$dep")
    done
  fi
  
  # Docker
  if [ -f "Dockerfile" ] || [ -f "docker-compose.yml" ]; then
    deps+=("docker")
  fi
  
  echo "${deps[@]}"
}

fetch_skill() {
  local name="$1"
  local prefer_full="${2:-false}"
  local output_dir="${SKILLS_DIR}/${name}"
  
  mkdir -p "$output_dir"
  
  # 1. Try local portfolio first (aiskills-repo)
  local local_path="aiskills-repo/skills/${name}"
  if [ ! -d "$local_path" ]; then
    local_path="../aiskills-repo/skills/${name}"
  fi
  
  if [ -d "$local_path" ] && [ -f "$local_path/SKILL.md" ]; then
    cp "$local_path/SKILL.md" "$output_dir/SKILL.md"
    log_success "Installed $name from local portfolio (aiskills-repo)"
    return 0
  fi

  # 2. Try llmstxt-cli first if available
  if command -v llmstxt &>/dev/null; then
    local flags=""
    [ "$prefer_full" = "true" ] && flags="--full"
    if llmstxt install "$name" $flags 2>/dev/null; then
      log_success "Installed $name via llmstxt-cli"
      return 0
    fi
  fi
  
  # Try npx llmstxt-cli
  if command -v npx &>/dev/null; then
    local flags=""
    [ "$prefer_full" = "true" ] && flags="--full"
    if npx llmstxt-cli install "$name" $flags 2>/dev/null; then
      log_success "Installed $name via npx llmstxt-cli"
      return 0
    fi
  fi
  
  # Direct fetch from known llms.txt URLs
  local urls=(
    "https://${name}.dev/llms.txt"
    "https://${name}.io/llms.txt"
    "https://${name}.com/llms.txt"
    "https://www.${name}.com/llms.txt"
    "https://docs.${name}.dev/llms.txt"
  )
  
  if [ "$prefer_full" = "true" ]; then
    local full_urls=()
    for url in "${urls[@]}"; do
      full_urls+=("${url%.txt}-full.txt")
    done
    urls=("${full_urls[@]}" "${urls[@]}")
  fi
  
  for url in "${urls[@]}"; do
    local content
    content=$(curl -sL --max-time 10 -o - -w "%{http_code}" "$url" 2>/dev/null)
    local http_code="000"
    local body=""
    if [ ${#content} -ge 3 ]; then
      http_code="${content: -3}"
      body="${content:0:${#content}-3}"
    fi
    
    if [ "$http_code" = "200" ] && [ ${#body} -gt 100 ]; then
      echo "$body" > "$output_dir/SKILL.md"
      log_success "Fetched $name from $url"
      return 0
    fi
  done
  
  log_warn "Could not find llms.txt for: $name"
  return 1
}

create_symlinks() {
  local skill_name="$1"
  shift
  local agents=("$@")
  
  local canonical_path="${SKILLS_DIR}/${skill_name}"
  
  for agent in "${agents[@]}"; do
    if [[ -v "SCOPED_AGENTS[$agent]" ]]; then
      local agent_skills_dir="${SCOPED_AGENTS[$agent]}"
      local target_dir="${agent_skills_dir}/${skill_name}"
      
      mkdir -p "$(dirname "$target_dir")"
      
      # Create relative symlink
      if [ ! -L "$target_dir" ] && [ ! -d "$target_dir" ]; then
        local rel_path
        rel_path=$(python3 -c "import os.path; print(os.path.relpath('$canonical_path', '$(dirname "$target_dir")'))" 2>/dev/null || echo "../../${canonical_path}")
        ln -s "$rel_path" "$target_dir" 2>/dev/null || cp -r "$canonical_path" "$target_dir"
      fi
    fi
  done
}

update_claude_md() {
  local skills=("$@")
  local claude_md="CLAUDE.md"
  
  # Create or update CLAUDE.md
  local skill_section="## AI Agent Skills\n\nThe following documentation skills are installed in \`.agents/skills/\`:\n"
  for skill in "${skills[@]}"; do
    if [ -f "${SKILLS_DIR}/${skill}/SKILL.md" ]; then
      local desc
      desc=$(head -20 "${SKILLS_DIR}/${skill}/SKILL.md" | grep -m1 'description:' | sed 's/description:\s*//' || echo "Documentation for ${skill}")
      skill_section+="- **${skill}**: ${desc}\n"
    fi
  done
  
  if [ -f "$claude_md" ]; then
    # Remove old skills section and append new one
    sed -i '/^## AI Agent Skills/,/^##[^#]/{ /^##[^#]/!d; }' "$claude_md" 2>/dev/null || true
    echo -e "\n${skill_section}" >> "$claude_md"
  else
    echo -e "${skill_section}" > "$claude_md"
  fi
  
  log_success "Updated CLAUDE.md with skill references"
}

# === Main ===

main() {
  local mode="detect"
  local skill_names=()
  local agents_filter=""
  local prefer_full=false
  local dry_run=false
  
  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case $1 in
      --detect) mode="detect"; shift ;;
      --install) mode="install"; shift; skill_names+=("$1"); shift ;;
      --agents) shift; agents_filter="$1"; shift ;;
      --full) prefer_full=true; shift ;;
      --dry-run) dry_run=true; shift ;;
      --help) 
        echo "Usage: bash install_skills.sh [--detect] [--install <name>] [--agents all] [--full] [--dry-run]"
        exit 0 ;;
      *) skill_names+=("$1"); shift ;;
    esac
  done
  
  print_header
  
  # Detect agents
  log_info "Detecting AI coding agents..."
  local detected_agents
  if [ "$agents_filter" = "all" ]; then
    detected_agents=($(echo "${!SCOPED_AGENTS[@]}" "${!UNIVERSAL_AGENTS[@]}"))
  elif [ -n "$agents_filter" ]; then
    IFS=',' read -ra detected_agents <<< "$agents_filter"
  else
    detected_agents=($(detect_agents))
  fi
  
  if [ ${#detected_agents[@]} -eq 0 ]; then
    log_warn "No AI agents detected. Installing to .agents/skills/ only."
    detected_agents=()
  else
    log_success "Detected ${#detected_agents[@]} agent(s): ${detected_agents[*]}"
  fi
  
  # Detect or use provided skill names
  if [ "$mode" = "detect" ] && [ ${#skill_names[@]} -eq 0 ]; then
    log_info "Scanning project dependencies..."
    skill_names=($(detect_dependencies))
    
    if [ ${#skill_names[@]} -eq 0 ]; then
      log_warn "No dependencies detected. Use --install <name> to install specific skills."
      exit 0
    fi
    
    log_info "Found ${#skill_names[@]} dependencies to check"
  fi
  
  if [ "$dry_run" = true ]; then
    echo -e "\n${YELLOW}DRY RUN — would install:${NC}"
    for name in "${skill_names[@]}"; do
      echo "  - $name → ${SKILLS_DIR}/${name}/SKILL.md"
    done
    echo -e "\n${YELLOW}For agents:${NC} ${detected_agents[*]}"
    exit 0
  fi
  
  # Install skills
  mkdir -p "$SKILLS_DIR"
  local installed=()
  
  for name in "${skill_names[@]}"; do
    if fetch_skill "$name" "$prefer_full"; then
      installed+=("$name")
      create_symlinks "$name" "${detected_agents[@]}"
    fi
  done
  
  # Update config files
  if [ ${#installed[@]} -gt 0 ]; then
    update_claude_md "${installed[@]}"
    
    echo -e "\n${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}  Installed ${#installed[@]} skill(s) successfully${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    for skill in "${installed[@]}"; do
      echo -e "  ${GREEN}✓${NC} $skill"
    done
    echo ""
  else
    log_warn "No skills were installed."
  fi
}

main "$@"
