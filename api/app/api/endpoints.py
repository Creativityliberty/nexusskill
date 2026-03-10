from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.db.models import Skill, Mission, ApiKey
from app.core.security import get_api_key, generate_api_key, hash_api_key
from sqlalchemy.orm import Session
from app.services.skill_ingestor import ingest_local_skills

router = APIRouter()

@router.get("/skills")
async def list_skills(api_key: str = Depends(get_api_key), db: Session = Depends(get_db)):
    skills = db.query(Skill).all()
    if not skills:
        return [
            {"name": "skill-creator", "description": "Guide for creating effective Claude Code skills."},
            {"name": "ui-style-generator", "description": "Generate a complete UI Design System."}
        ]
    return skills

@router.post("/skills/sync")
async def sync_skills(api_key: str = Depends(get_api_key)):
    try:
        # Check current working directory for debugging
        import os
        cwd = os.getcwd()
        print(f"Current working directory: {cwd}")
        
        # Try finding aiskills-repo relative to API root
        count = ingest_local_skills("aiskills-repo/skills")
        return {"status": "success", "message": f"Successfully synchronized {count} skills from repository"}
    except Exception as e:
        print(f"Sync error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/missions")
async def list_missions(api_key: str = Depends(get_api_key), db: Session = Depends(get_db)):
    return db.query(Mission).order_by(Mission.created_at.desc()).all()

@router.get("/keys")
async def list_keys(api_key: str = Depends(get_api_key), db: Session = Depends(get_db)):
    return db.query(ApiKey).all()

@router.post("/keys/generate")
async def create_key(name: str = "New Key", api_key: str = Depends(get_api_key), db: Session = Depends(get_db)):
    raw_key = generate_api_key()
    hashed = hash_api_key(raw_key)
    
    new_key = ApiKey(
        key_hash=hashed,
        name=name
    )
    db.add(new_key)
    db.commit()
    
    return {
        "name": name,
        "key": raw_key,
        "message": "Store this key safely. It will not be shown again."
    }

@router.post("/mission/plan")
async def plan_mission(goal: str, api_key: str = Depends(get_api_key), db: Session = Depends(get_db)):
    # Simple planning logic for Phase 2
    new_mission = Mission(
        title=f"Mission: {goal[:30]}...",
        description=goal,
        status="planned"
    )
    db.add(new_mission)
    db.commit()
    db.refresh(new_mission)
    
    return {
        "mission_id": f"m_{new_mission.id}",
        "status": new_mission.status,
        "goal": goal,
        "tasks": [
            {"id": "t1", "action": "Research market", "skill": "context-builder"},
            {"id": "t2", "action": "Generate styleguide", "skill": "ui-style-generator"}
        ]
    }
