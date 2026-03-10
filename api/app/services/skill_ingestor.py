import os
from sqlalchemy.orm import Session
from app.db.models import Skill
from app.db.base import SessionLocal
import yaml

def ingest_local_skills(repo_path: str = "../../aiskills-repo/skills"):
    """
    Scans the local aiskills-repo and populates the database cache.
    """
    db = SessionLocal()
    try:
        if not os.path.exists(repo_path):
            raise FileNotFoundError(f"Skill repository not found at: {os.path.abspath(repo_path)}")
            
        print(f"Scanning skills in: {os.path.abspath(repo_path)}")
        count = 0
            skill_path = os.path.join(repo_path, skill_dir)
            if not os.path.isdir(skill_path):
                continue
                
            skill_file = os.path.join(skill_path, "SKILL.md")
            if not os.path.exists(skill_file):
                continue
                
            with open(skill_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Basic parsing of frontmatter
            try:
                parts = content.split("---")
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    description = metadata.get("description", "")
                    name = metadata.get("name", skill_dir)
                else:
                    name = skill_dir
                    description = ""
            except Exception as e:
                print(f"Error parsing {skill_dir}: {e}")
                name = skill_dir
                description = ""

            # Update or Create in DB
            db_skill = db.query(Skill).filter(Skill.name == name).first()
            if db_skill:
                db_skill.description = description
                db_skill.content = content
            else:
                new_skill = Skill(
                    name=name,
                    description=description,
                    content=content
                )
                db.add(new_skill)
            count += 1
        
        db.commit()
        print(f"Skill ingestion complete. {count} skills synchronized.")
        return count
    finally:
        db.close()

if __name__ == "__main__":
    # To run manually: python -m app.services.skill_ingestor
    ingest_local_skills()
