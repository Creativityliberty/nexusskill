from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.core.security import get_api_key
from app.db.base import get_db
from app.db.models import Skill, Mission
from sqlalchemy.orm import Session

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

@router.get("/missions")
async def list_missions(api_key: str = Depends(get_api_key), db: Session = Depends(get_db)):
    return db.query(Mission).order_by(Mission.created_at.desc()).all()

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
