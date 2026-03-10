---
name: ui-style-generator
description: Generate a complete UI Design System and Styleguide from a project description. Produces color tokens (light/dark), typography, spacing, animations, layout, shadows, border radius, gradients, and a full CSS variables export. Use when the user wants to generate a design system, create a styleguide, define UI tokens, or bootstrap the visual identity of a project. Triggers on "generate a design system", "create a styleguide", "generate UI tokens", "make a UI style for my app", "/ui-style-generator".
---

# UI Style Generator

Generate a complete, production-ready UI Design System from a project description.
Claude generates the design system JSON, then the bundled script formats it into a Markdown styleguide with CSS variables.

## Workflow

### 1. Understand the Project

Ask the user (if not already provided):
- **What is the project?** (e.g. "a fintech dashboard", "a meditation app", "a gaming platform")
- **Visual vibe?** (e.g. "minimal", "bold", "glassmorphism", "dark cyberpunk", "warm & friendly")
- **Primary color preference?** (optional — Claude will choose if not given)

### 2. Generate the DesignSystem JSON

Generate a complete JSON object following the schema in [references/design-system-schema.md](references/design-system-schema.md).

Key design principles:
- **Light + Dark palettes** must be cohesive and distinct
- **Gradients** must be valid CSS `linear-gradient()` strings
- **Shadows** must be valid CSS `box-shadow` values
- **Colors** must be valid hex codes
- **Typography**: choose a real Google Font that matches the vibe
- **Aesthetic consistency**: every token should reinforce the same visual identity

Output the full JSON in a code block so the user can inspect it.

### 3. Format as Markdown Styleguide

Use the bundled script to convert JSON → Markdown:

```bash
# If the project uses Node/TypeScript:
npx tsx skills/ui-style-generator/scripts/generate_markdown.ts design-system.json

# Or generate directly inline — use the template in references/markdown-template.md
```

If no Node environment is available, generate the Markdown directly using the template in [references/markdown-template.md](references/markdown-template.md).

### 4. Save the Output

```bash
# Save JSON tokens
cat > design-system.json << 'EOF'
{ ...generated JSON... }
EOF

# Save Markdown styleguide
cat > STYLEGUIDE.md << 'EOF'
...generated markdown...
EOF
```

### 5. Show the Result

Present:
- The Markdown styleguide inline
- The CSS variables block (extracted from the styleguide)
- File paths where files were saved

## Wrap Up

- ✅ Design system generated for: `<project name>`
- ✅ Saved: `design-system.json` + `STYLEGUIDE.md`
- Color palette: light mode primary `<hex>`, dark mode `<hex>`
- Font: `<font-family>`
- Ask: "Do you want me to adjust any tokens (colors, spacing, fonts)?"
