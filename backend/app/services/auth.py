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
        email = data.email.strip().lower()
        username = data.username.strip()
        password_hash = hash_password(data.password)

        existing_user = self.users.get_by_email(email)

        username_owner = self.users.get_by_username(username)
        if username_owner is not None and (
            existing_user is None or username_owner.id != existing_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        login_owner = self.users.get_by_login(username)
        if login_owner is not None and (
            existing_user is None or login_owner.id != existing_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login already exists",
            )

        if existing_user is not None:
            if existing_user.email_verified_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists",
                )

            user = self.users.update_unverified_user_registration(
                existing_user,
                username=username,
                login=username,
                password_hash=password_hash,
            )
            self.db.commit()
            self.db.refresh(user)
            return user

        user = self.users.create_user(
            username=username,
            email=email,
            login=username,
            password_hash=password_hash,
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

        if user.email_verified_at is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email is not verified",
            )

        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return user