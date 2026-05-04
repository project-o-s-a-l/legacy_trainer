from fastapi import APIRouter, Depends

from backend.app.api.dependencies.auth import get_current_user
from backend.app.models.user import User
from backend.app.schemas.user import UserMeResponse


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserMeResponse:
    return UserMeResponse(
        username=current_user.username,
        email=current_user.email,
        points=current_user.total_score,
        memberSince=current_user.created_at,
        lastSeen=current_user.last_login_at,
        avatarUrl=current_user.avatar_url,
        isOnline=False,
    )
