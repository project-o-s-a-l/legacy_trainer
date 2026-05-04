from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.repositories.user import UserRepository
from backend.app.schemas.auth import LoginRequest, RegisterRequest
from backend.app.services.security import hash_password, verify_password


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, data: RegisterRequest) -> User:
        if self.users.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

        if self.users.get_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        if self.users.get_by_login(data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login already exists",
            )

        user = self.users.create_user(
            username=data.username,
            email=data.email,
            login=data.username,
            password_hash=hash_password(data.password),
        )

        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, data: LoginRequest) -> User:
        user = self.users.get_by_email(data.login)
        if user is None:
            user = self.users.get_by_login(data.login)

        if user is None or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return user
