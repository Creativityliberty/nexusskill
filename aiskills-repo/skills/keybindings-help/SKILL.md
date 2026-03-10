---
name: keybindings-help
description: Use when the user wants to customize keyboard shortcuts, rebind keys, add chord bindings, or modify ~/.claude/keybindings.json. Examples: "rebind ctrl+s", "add a chord shortcut", "change the submit key", "customize keybindings".
---

# Keybindings Customization Skill

Help users customize Claude Code keyboard shortcuts by modifying `~/.claude/keybindings.json`.

## Keybindings File Location

```
~/.claude/keybindings.json
```

Create if it doesn't exist. This file overrides default Claude Code keybindings.

## File Format

```json
[
  {
    "key": "ctrl+shift+enter",
    "command": "claude.sendMessage"
  },
  {
    "key": "ctrl+k ctrl+c",
    "command": "claude.clearConversation"
  }
]
```

## Common Commands

| Command | Description |
|---------|-------------|
| `claude.sendMessage` | Submit the current message |
| `claude.clearConversation` | Clear the conversation |
| `claude.newConversation` | Start a new conversation |
| `claude.toggleSidebar` | Toggle the sidebar |
| `claude.focusInput` | Focus the input field |
| `claude.stopGeneration` | Stop current generation |

## Key Syntax

- Single keys: `"ctrl+s"`, `"alt+enter"`, `"shift+f5"`
- Chord bindings (two-step): `"ctrl+k ctrl+s"` (press Ctrl+K then Ctrl+S)
- Function keys: `"f1"` through `"f12"`
- Special keys: `"escape"`, `"tab"`, `"backspace"`, `"delete"`, `"enter"`

## Workflow

Make a todo list for all the tasks in this workflow.

### 1. Understand the Request

Ask the user:
- What action do they want to bind/rebind?
- What key combination do they want to use?
- Is it a single shortcut or a chord (two-step) binding?

### 2. Read Existing Keybindings

```bash
cat ~/.claude/keybindings.json 2>/dev/null || echo "[]"
```

If the file doesn't exist, start with an empty array `[]`.

### 3. Check for Conflicts

- Look for existing bindings that use the same key combination
- Warn the user if a conflict is found
- Ask if they want to override the existing binding

### 4. Update Keybindings File

Add or modify the keybinding entry. For example, to rebind submit to `ctrl+enter`:

```json
[
  {
    "key": "ctrl+enter",
    "command": "claude.sendMessage"
  }
]
```

For chord bindings (two-step shortcuts):
```json
[
  {
    "key": "ctrl+k s",
    "command": "claude.sendMessage"
  }
]
```

### 5. Write the File

```bash
cat > ~/.claude/keybindings.json << 'EOF'
[
  {
    "key": "YOUR_KEY_HERE",
    "command": "YOUR_COMMAND_HERE"
  }
]
EOF
```

### 6. Confirm with User

Inform the user:
- The new keybinding that was set
- That changes take effect immediately (no restart needed)
- How to test the new binding

## Wrap Up

Provide a summary:
- ✅ Keybinding added/modified
- The key combination and what it does
- Any conflicts that were resolved
- How to revert if needed: restore the previous `~/.claude/keybindings.json` content
