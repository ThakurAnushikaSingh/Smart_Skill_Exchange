from fastapi import APIRouter, Depends, status

from app.core.security import get_current_user
from app.schemas.skills import SkillCreateRequest
from app.services.skill_service import SkillService

router = APIRouter(tags=["skills"])


@router.post("/skills/add", status_code=status.HTTP_201_CREATED)
def add_skill(payload: SkillCreateRequest, current_user: dict = Depends(get_current_user)):
    return SkillService.add_skill(current_user, payload)


@router.get("/skills")
def list_skills():
    return SkillService.list_skills()
