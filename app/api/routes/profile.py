from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.services.profile_service import ProfileService

router = APIRouter(tags=["profile"])


@router.get("/profile", response_model=ProfileResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
    return ProfileService.get_profile(current_user)


@router.post("/profile/update", response_model=ProfileResponse)
def update_profile(payload: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    return ProfileService.update_profile(current_user, payload)
