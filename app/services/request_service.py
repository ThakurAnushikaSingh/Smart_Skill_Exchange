from fastapi import status

from app.db.supabase_client import get_supabase_client
from app.schemas.requests import MatchCreateRequest, MessageCreateRequest, SkillRequestCreate
from app.services.base import ServiceError

VALID_REQUEST_STATUS = {"open", "matched", "completed"}
VALID_MATCH_STATUS = {"pending", "active", "completed", "cancelled"}


class RequestService:
    @staticmethod
    def create_request(current_user: dict, payload: SkillRequestCreate) -> dict:
        supabase = get_supabase_client()
        row = {
            "requester_id": current_user["id"],
            "skill_name": payload.skill_name.strip(),
            "description": payload.description.strip(),
            "status": "open",
        }

        try:
            result = supabase.table("skill_requests").insert(row).execute()
        except Exception as exc:
            raise ServiceError("Unable to create request", status.HTTP_502_BAD_GATEWAY) from exc

        if not result.data:
            raise ServiceError("Request insert returned no data", status.HTTP_500_INTERNAL_SERVER_ERROR)

        return result.data[0]

    @staticmethod
    def list_requests(status_filter: str | None = None) -> list[dict]:
        supabase = get_supabase_client()
        query = supabase.table("skill_requests").select("*").order("created_at", desc=True)

        if status_filter:
            if status_filter not in VALID_REQUEST_STATUS:
                raise ServiceError("Invalid request status filter", status.HTTP_422_UNPROCESSABLE_ENTITY)
            query = query.eq("status", status_filter)

        try:
            result = query.execute()
        except Exception as exc:
            raise ServiceError("Unable to list requests", status.HTTP_502_BAD_GATEWAY) from exc

        return result.data or []


class MatchService:
    @staticmethod
    def create_match(current_user: dict, payload: MatchCreateRequest) -> dict:
        supabase = get_supabase_client()

        try:
            req_res = (
                supabase.table("skill_requests")
                .select("id, requester_id, status")
                .eq("id", payload.request_id)
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise ServiceError("Unable to validate request", status.HTTP_502_BAD_GATEWAY) from exc

        request_row = req_res.data[0] if req_res.data else None
        if not request_row:
            raise ServiceError("Skill request not found", status.HTTP_404_NOT_FOUND)
        if request_row["status"] != "open":
            raise ServiceError("Only open requests can be matched", status.HTTP_409_CONFLICT)
        if request_row["requester_id"] == payload.provider_id:
            raise ServiceError("Requester and provider cannot be the same", status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            dup_res = (
                supabase.table("matches")
                .select("id")
                .eq("skill_request_id", payload.request_id)
                .eq("provider_id", payload.provider_id)
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise ServiceError("Unable to check duplicate matches", status.HTTP_502_BAD_GATEWAY) from exc

        if dup_res.data:
            raise ServiceError("Match already exists for this provider and request", status.HTTP_409_CONFLICT)

        row = {
            "requester_id": request_row["requester_id"],
            "provider_id": payload.provider_id,
            "skill_request_id": payload.request_id,
            "status": "pending",
            "created_by": current_user["id"],
        }

        try:
            match_res = supabase.table("matches").insert(row).execute()
            supabase.table("skill_requests").update({"status": "matched"}).eq("id", payload.request_id).execute()
        except Exception as exc:
            raise ServiceError("Unable to create match", status.HTTP_502_BAD_GATEWAY) from exc

        if not match_res.data:
            raise ServiceError("Match insert returned no data", status.HTTP_500_INTERNAL_SERVER_ERROR)

        return match_res.data[0]

    @staticmethod
    def list_matches(current_user: dict, status_filter: str | None = None) -> list[dict]:
        supabase = get_supabase_client()
        query = (
            supabase.table("matches")
            .select("*")
            .or_(f"requester_id.eq.{current_user['id']},provider_id.eq.{current_user['id']}")
            .order("created_at", desc=True)
        )

        if status_filter:
            if status_filter not in VALID_MATCH_STATUS:
                raise ServiceError("Invalid match status filter", status.HTTP_422_UNPROCESSABLE_ENTITY)
            query = query.eq("status", status_filter)

        try:
            result = query.execute()
        except Exception as exc:
            raise ServiceError("Unable to list matches", status.HTTP_502_BAD_GATEWAY) from exc

        return result.data or []


class MessageService:
    @staticmethod
    def send_message(current_user: dict, payload: MessageCreateRequest) -> dict:
        if payload.receiver_id == current_user["id"]:
            raise ServiceError("Cannot message yourself", status.HTTP_422_UNPROCESSABLE_ENTITY)

        supabase = get_supabase_client()
        row = {
            "sender_id": current_user["id"],
            "receiver_id": payload.receiver_id,
            "message": payload.message.strip(),
        }

        try:
            result = supabase.table("messages").insert(row).execute()
        except Exception as exc:
            raise ServiceError("Unable to send message", status.HTTP_502_BAD_GATEWAY) from exc

        if not result.data:
            raise ServiceError("Message insert returned no data", status.HTTP_500_INTERNAL_SERVER_ERROR)

        return result.data[0]
