from fastapi import APIRouter, status

from app.schemas.auth import AuthResponse, LoginRequest, SignupRequest
from app.services.auth_service import AuthService

router = APIRouter(tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest):
    return AuthService.signup(payload)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    return AuthService.login(payload)
