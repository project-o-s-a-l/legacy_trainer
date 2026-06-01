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
    cookie_secure: bool = os.getenv("COOKIE_SECURE", "true").lower() == "true"
    frontend_origins: list[str] = _split_csv(
        os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5173,https://localhost:5173,"
            "http://localhost:3000,https://localhost:3000",
        )
    )
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    smtp_timeout_seconds: int = int(os.getenv("SMTP_TIMEOUT_SECONDS", "10"))
    verification_code_ttl_minutes: int = int(
        os.getenv("VERIFICATION_CODE_TTL_MINUTES", "10")
    )
    password_reset_token_ttl_minutes: int = int(
        os.getenv("PASSWORD_RESET_TOKEN_TTL_MINUTES", "30")
    )


settings = Settings()