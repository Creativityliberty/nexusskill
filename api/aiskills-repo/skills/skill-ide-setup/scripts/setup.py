import os
import argparse
import pathlib

TEMPLATES = {
    "cursor": {
        "path": ".cursor/rules/aiskills.md",
        "legacy": ".cursorrules"
    },
    "windsurf": {
        "path": ".windsurf/rules/aiskills.md",
        "legacy": ".windsurfrules"
    },
    "trae": {
        "path": ".trae/rules/project_rules.md",
        "legacy": None
    },
    "cline": {
        "path": ".clinerules",
        "legacy": None
    },
    "roo": {
        "path": ".clinerules",
        "legacy": None
    },
    "antigravity": {
        "path": ".agent/rules/aiskills.md",
        "legacy": None
    }
}

def setup_ide(ide_name, workspace_root="."):
    if ide_name not in TEMPLATES:
        print(f"Error: IDE '{ide_name}' not supported.")
        return

    config = TEMPLATES[ide_name]
    root = pathlib.Path(workspace_root)
    
    # Read template - Relative to the script location
    script_dir = pathlib.Path(__file__).parent.parent
    template_path = script_dir / "templates" / "base_rules.md"
    
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        return
        
    content = template_path.read_text(encoding="utf-8")
    
    # Target path
    target_path = root / config["path"]
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Writing rules to {target_path}...")
    target_path.write_text(content, encoding="utf-8")
    
    # Handle legacy if it exists
    if config["legacy"]:
        legacy_path = root / config["legacy"]
        if legacy_path.exists():
            print(f"Updating legacy file {legacy_path}...")
            # Append if not present
            old_content = legacy_path.read_text(encoding="utf-8")
            if "aiskills" not in old_content:
                legacy_path.write_text(old_content + "\n\n" + content, encoding="utf-8")
        else:
            # Create legacy file too for maximum compatibility
            print(f"Creating legacy file {legacy_path}...")
            legacy_path.write_text(content, encoding="utf-8")

    print(f"✅ Setup complete for {ide_name}!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup IDE rules for a project.")
    parser.add_argument("--ide", required=True, choices=TEMPLATES.keys(), help="The IDE to setup.")
    parser.add_argument("--root", default=".", help="The workspace root directory.")
    
    args = parser.parse_args()
    setup_ide(args.ide, args.root)
