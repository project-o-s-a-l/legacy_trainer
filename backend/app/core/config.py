import os


class Settings:
    """Application settings loaded from environment variables."""

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:2206@localhost:5432/legacy_trainer_db",
    )
    db_echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"


settings = Settings()
