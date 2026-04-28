from fastapi import status

from app.db.supabase_client import get_supabase_client
from app.schemas.auth import LoginRequest, SignupRequest
from app.services.base import ServiceError


class AuthService:
    @staticmethod
    def signup(payload: SignupRequest) -> dict:
        supabase = get_supabase_client()

        try:
            auth_response = supabase.auth.sign_up(
                {
                    "email": payload.email,
                    "password": payload.password,
                    "options": {"data": {"name": payload.name}},
                }
            )
        except Exception as exc:
            raise ServiceError("Supabase signup failed", status.HTTP_502_BAD_GATEWAY) from exc

        auth_user = getattr(auth_response, "user", None)
        session = getattr(auth_response, "session", None)
        if auth_user is None:
            raise ServiceError("Could not create auth user", status.HTTP_400_BAD_REQUEST)

        profile_insert = {
            "id": auth_user.id,
            "email": payload.email,
            "name": payload.name,
        }

        try:
            supabase.table("users").upsert(profile_insert).execute()
        except Exception as exc:
            raise ServiceError("Auth created but user profile insert failed", status.HTTP_502_BAD_GATEWAY) from exc

        return {
            "user_id": auth_user.id,
            "email": payload.email,
            "access_token": getattr(session, "access_token", None),
            "refresh_token": getattr(session, "refresh_token", None),
        }

    @staticmethod
    def login(payload: LoginRequest) -> dict:
        supabase = get_supabase_client()
        try:
            auth_response = supabase.auth.sign_in_with_password(
                {"email": payload.email, "password": payload.password}
            )
        except Exception as exc:
            raise ServiceError("Invalid credentials", status.HTTP_401_UNAUTHORIZED) from exc

        auth_user = getattr(auth_response, "user", None)
        session = getattr(auth_response, "session", None)
        if auth_user is None or session is None:
            raise ServiceError("Login failed", status.HTTP_401_UNAUTHORIZED)

        return {
            "user_id": auth_user.id,
            "email": auth_user.email,
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        }
