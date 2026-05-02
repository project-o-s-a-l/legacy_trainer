import os

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    """Application settings loaded from environment variables."""

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:admin@localhost:5432/legacy_trainer_db",
    )
    db_echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    secret_key: str = os.getenv("SECRET_KEY", "change_me")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    frontend_origins: list[str] = _split_csv(
        os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5173,https://localhost:5173,"
            "http://localhost:3000,https://localhost:3000",
        )
    )


settings = Settings()
