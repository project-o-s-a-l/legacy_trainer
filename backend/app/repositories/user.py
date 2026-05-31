from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.scalar(stmt)

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.db.scalar(stmt)

    def get_by_login(self, login: str) -> User | None:
        stmt = select(User).where(User.login == login)
        return self.db.scalar(stmt)

    def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self.db.scalar(stmt)

    def create_user(
        self,
        *,
        username: str,
        email: str,
        login: str,
        password_hash: str,
    ) -> User:
        user = User(
            username=username,
            email=email,
            login=login,
            password_hash=password_hash,
            email_verified_at=None,
        )
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def mark_email_as_verified(self, user: User) -> None:
        user.email_verified_at = datetime.now(timezone.utc)

    def is_email_verified(self, user: User) -> bool:
        return user.email_verified_at is not None