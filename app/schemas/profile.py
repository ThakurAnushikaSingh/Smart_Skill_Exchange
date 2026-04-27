from pydantic import BaseModel, Field


class ProfileUpdateRequest(BaseModel):
    bio: str | None = Field(default=None, max_length=1500)
    skills_offered: list[str] = Field(default_factory=list, max_length=100)
    skills_wanted: list[str] = Field(default_factory=list, max_length=100)


class ProfileResponse(BaseModel):
    user_id: str
    email: str
    name: str | None
    bio: str | None
    skills_offered: list[str]
    skills_wanted: list[str]
