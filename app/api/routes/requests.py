from fastapi import APIRouter, Depends, Query, status

from app.core.security import get_current_user
from app.schemas.requests import MatchCreateRequest, MessageCreateRequest, SkillRequestCreate
from app.services.request_service import MatchService, MessageService, RequestService

router = APIRouter(tags=["requests"])


@router.post("/request", status_code=status.HTTP_201_CREATED)
def create_request(payload: SkillRequestCreate, current_user: dict = Depends(get_current_user)):
    return RequestService.create_request(current_user, payload)


@router.get("/requests")
def list_requests(status: str | None = Query(default=None)):
    return RequestService.list_requests(status)


@router.post("/match", status_code=status.HTTP_201_CREATED)
def create_match(payload: MatchCreateRequest, current_user: dict = Depends(get_current_user)):
    return MatchService.create_match(current_user, payload)


@router.get("/matches")
def list_matches(
    status: str | None = Query(default=None), current_user: dict = Depends(get_current_user)
):
    return MatchService.list_matches(current_user, status)


@router.post("/messages", status_code=status.HTTP_201_CREATED)
def send_message(payload: MessageCreateRequest, current_user: dict = Depends(get_current_user)):
    return MessageService.send_message(current_user, payload)
