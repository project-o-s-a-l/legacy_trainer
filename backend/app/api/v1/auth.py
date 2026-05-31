from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LoginUserResponse,
    MessageResponse,
    RegisterRequest,
    RegisterResponse,
)
from backend.app.schemas.user import UserShortResponse
from backend.app.schemas.verification import (
    RequestVerificationCodeRequest,
    RequestVerificationCodeResponse,
)
from backend.app.services.auth import AuthService
from backend.app.services.token import create_access_token
from backend.app.services.verification import VerificationService


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(data: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    user = AuthService(db).register(data)
    return RegisterResponse(
        user=UserShortResponse.model_validate(user),
    )


@router.post(
    "/request-verification-code",
    response_model=RequestVerificationCodeResponse,
)
def request_verification_code(
    data: RequestVerificationCodeRequest,
    db: Session = Depends(get_db),
) -> RequestVerificationCodeResponse:
    return VerificationService(db).request_code(data)


@router.post("/login", response_model=LoginResponse)
def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    user = AuthService(db).login(data)
    token = create_access_token(user.id)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=True,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )

    return LoginResponse(
        token=token,
        user=LoginUserResponse(
            id=user.id,
            login=user.login,
        ),
    )


@router.post("/logout", response_model=MessageResponse)
def logout(response: Response) -> MessageResponse:
    response.delete_cookie(key="access_token", path="/")
    return MessageResponse(message="Logged out")