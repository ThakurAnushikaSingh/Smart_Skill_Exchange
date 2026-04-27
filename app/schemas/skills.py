from pydantic import BaseModel, Field


class SkillCreateRequest(BaseModel):
    skill_name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1500)


class SkillResponse(BaseModel):
    id: str
    user_id: str
    skill_name: str
    description: str | None
    created_at: str
