from fastapi import status

from app.db.supabase_client import get_supabase_client
from app.schemas.profile import ProfileUpdateRequest
from app.services.base import ServiceError


class ProfileService:
    @staticmethod
    def get_profile(current_user: dict) -> dict:
        supabase = get_supabase_client()

        try:
            user_res = (
                supabase.table("users")
                .select("id,email,name")
                .eq("id", current_user["id"])
                .limit(1)
                .execute()
            )
            profile_res = (
                supabase.table("profiles")
                .select("bio,skills_offered,skills_wanted")
                .eq("user_id", current_user["id"])
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise ServiceError("Unable to fetch profile", status.HTTP_502_BAD_GATEWAY) from exc

        user_row = user_res.data[0] if user_res.data else None
        if not user_row:
            raise ServiceError("User record not found", status.HTTP_404_NOT_FOUND)

        profile_row = profile_res.data[0] if profile_res.data else {}
        return {
            "user_id": user_row["id"],
            "email": user_row["email"],
            "name": user_row.get("name"),
            "bio": profile_row.get("bio"),
            "skills_offered": profile_row.get("skills_offered") or [],
            "skills_wanted": profile_row.get("skills_wanted") or [],
        }

    @staticmethod
    def update_profile(current_user: dict, payload: ProfileUpdateRequest) -> dict:
        supabase = get_supabase_client()

        if not payload.skills_offered and not payload.skills_wanted and payload.bio is None:
            raise ServiceError("At least one profile field is required", status.HTTP_422_UNPROCESSABLE_ENTITY)

        update_data = {
            "user_id": current_user["id"],
            "bio": payload.bio,
            "skills_offered": payload.skills_offered,
            "skills_wanted": payload.skills_wanted,
        }

        try:
            supabase.table("profiles").upsert(update_data).execute()
        except Exception as exc:
            raise ServiceError("Unable to update profile", status.HTTP_502_BAD_GATEWAY) from exc

        return ProfileService.get_profile(current_user)
