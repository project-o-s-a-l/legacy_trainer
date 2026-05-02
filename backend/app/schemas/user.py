from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserShortResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserMeResponse(BaseModel):
    username: str
    email: EmailStr
    points: int
    memberSince: datetime
    lastSeen: datetime | None = None
    avatarUrl: str | None = None
    isOnline: bool = False
