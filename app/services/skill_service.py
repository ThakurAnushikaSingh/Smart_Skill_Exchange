from fastapi import status

from app.db.supabase_client import get_supabase_client
from app.schemas.skills import SkillCreateRequest
from app.services.base import ServiceError


class SkillService:
    @staticmethod
    def add_skill(current_user: dict, payload: SkillCreateRequest) -> dict:
        supabase = get_supabase_client()

        row = {
            "user_id": current_user["id"],
            "skill_name": payload.skill_name.strip(),
            "description": payload.description,
        }

        try:
            result = supabase.table("skills").insert(row).execute()
        except Exception as exc:
            raise ServiceError("Unable to add skill", status.HTTP_502_BAD_GATEWAY) from exc

        if not result.data:
            raise ServiceError("Skill insert returned no data", status.HTTP_500_INTERNAL_SERVER_ERROR)

        return result.data[0]

    @staticmethod
    def list_skills() -> list[dict]:
        supabase = get_supabase_client()

        try:
            result = supabase.table("skills").select("*").order("created_at", desc=True).execute()
        except Exception as exc:
            raise ServiceError("Unable to list skills", status.HTTP_502_BAD_GATEWAY) from exc

        return result.data or []
