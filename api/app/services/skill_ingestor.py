import os
from sqlalchemy.orm import Session
from app.db.models import Skill
from app.db.base import SessionLocal
import yaml

def ingest_local_skills(repo_path: str = None):
    """
    Scans for aiskills-repo and populates the database.
    """
    db = SessionLocal()
    try:
        # 1. Path Discovery
        search_paths = [
            repo_path,
            "api/aiskills-repo/skills",
            "aiskills-repo/skills",
            "../aiskills-repo/skills",
            "/var/task/api/aiskills-repo/skills",
            "/var/task/aiskills-repo/skills"
        ]
        
        actual_path = None
        for p in search_paths:
            if p and os.path.exists(p) and os.path.isdir(p):
                actual_path = p
                break
        
        if not actual_path:
            # Last ditch: search for it
            cwd = os.getcwd()
            for root, dirs, files in os.walk(cwd):
                if "aiskills-repo" in dirs:
                    pot_path = os.path.join(root, "aiskills-repo", "skills")
                    if os.path.exists(pot_path):
                        actual_path = pot_path
                        break
                if root.count(os.sep) - cwd.count(os.sep) > 3:
                    continue

        if not actual_path:
            raise FileNotFoundError(f"Could not locate 'aiskills-repo/skills' in {os.getcwd()}. Paths checked: {search_paths}")

        print(f"Ingesting skills from: {os.path.abspath(actual_path)}")
        
        count = 0
        for skill_dir in os.listdir(actual_path):
            skill_path = os.path.join(actual_path, skill_dir)
            if not os.path.isdir(skill_path):
                continue
                
            skill_file = os.path.join(skill_path, "SKILL.md")
            if not os.path.exists(skill_file):
                skill_file = os.path.join(skill_path, "skill.md")
                if not os.path.exists(skill_file):
                    continue
                
            with open(skill_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            name = skill_dir
            description = ""
            try:
                if content.startswith("---"):
                    parts = content.split("---")
                    if len(parts) >= 3:
                        metadata = yaml.safe_load(parts[1])
                        description = metadata.get("description", "")
                        name = metadata.get("name", skill_dir)
            except Exception as e:
                print(f"Metadata parse error in {skill_dir}: {e}")

            db_skill = db.query(Skill).filter(Skill.name == name).first()
            if db_skill:
                db_skill.description = description
                db_skill.content = content
            else:
                db_skill = Skill(name=name, description=description, content=content)
                db.add(db_skill)
            count += 1
        
        db.commit()
        return count
    finally:
        db.close()

if __name__ == "__main__":
    # To run manually: python -m app.services.skill_ingestor
    ingest_local_skills()
