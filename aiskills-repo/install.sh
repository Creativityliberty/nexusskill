#!/bin/bash
# AI Skills Collection - Install Script
# Copies skills into ~/.claude/skills/ for use in Claude Code

set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/skills" && pwd)"
TARGET_DIR="$HOME/.claude/skills"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "AI Skills Collection - Installer"
echo "================================="
echo ""

# Create target dir if needed
mkdir -p "$TARGET_DIR"

# List available skills
SKILLS=($(ls "$SKILLS_DIR"))

if [ ${#SKILLS[@]} -eq 0 ]; then
  echo "No skills found in $SKILLS_DIR"
  exit 1
fi

echo "Available skills:"
for skill in "${SKILLS[@]}"; do
  echo "  - $skill"
done
echo ""

# Install mode: all or specific
if [ "${1:-}" = "--all" ]; then
  TO_INSTALL=("${SKILLS[@]}")
elif [ -n "${1:-}" ]; then
  TO_INSTALL=("$1")
else
  # Interactive: ask which to install
  echo "Install options:"
  echo "  ./install.sh --all          Install all skills"
  echo "  ./install.sh <skill-name>   Install a specific skill"
  echo ""
  echo "Installing all skills by default..."
  TO_INSTALL=("${SKILLS[@]}")
fi

# Install each skill
for skill in "${TO_INSTALL[@]}"; do
  src="$SKILLS_DIR/$skill"
  dst="$TARGET_DIR/$skill"

  if [ ! -d "$src" ]; then
    echo -e "${YELLOW}Warning: Skill '$skill' not found, skipping.${NC}"
    continue
  fi

  mkdir -p "$dst"
  cp -r "$src/." "$dst/"
  echo -e "${GREEN}✅ Installed: $skill${NC}"
done

echo ""
echo "Done! Skills installed to $TARGET_DIR"
echo "Restart Claude Code to use the new skills."
