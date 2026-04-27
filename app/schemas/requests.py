from pydantic import BaseModel, Field


class SkillRequestCreate(BaseModel):
    skill_name: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=5, max_length=1500)


class MatchCreateRequest(BaseModel):
    request_id: str
    provider_id: str


class MessageCreateRequest(BaseModel):
    receiver_id: str
    message: str = Field(min_length=1, max_length=4000)
