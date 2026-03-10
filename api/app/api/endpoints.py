from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.core.security import get_api_key

router = APIRouter()

@router.get("/skills")
async def list_skills(api_key: str = Depends(get_api_key)):
    # Mock data for Phase 1
    return [
        {"name": "skill-creator", "description": "Guide for creating effective Claude Code skills."},
        {"name": "ui-style-generator", "description": "Generate a complete UI Design System."}
    ]

@router.post("/mission/plan")
async def plan_mission(goal: str, api_key: str = Depends(get_api_key)):
    return {
        "mission_id": "m_123",
        "status": "planned",
        "goal": goal,
        "tasks": [
            {"id": "t1", "action": "Research market", "skill": "context-builder"},
            {"id": "t2", "action": "Generate styleguide", "skill": "ui-style-generator"}
        ]
    }
