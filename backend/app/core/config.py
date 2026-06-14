import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _get_bool(name: str, default: str) -> bool:
    return os.getenv(name, default).lower() == "true"

def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(f"Environment variable {name} is required")
    return value

def _get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url is not None and database_url.strip():
        return database_url

    db_name = os.getenv("POSTGRES_DB", "").strip()
    db_user = os.getenv("POSTGRES_USER", "").strip()
    if not db_name or not db_user:
        raise RuntimeError(
            "Environment variable DATABASE_URL is required, "
            "or provide POSTGRES_DB and POSTGRES_USER for local fallback"
        )

    db_password = os.getenv("POSTGRES_PASSWORD", "")
    db_host = os.getenv("POSTGRES_HOST", "localhost").strip() or "localhost"
    db_port = os.getenv("POSTGRES_PORT", "5432").strip() or "5432"

    quoted_user = quote_plus(db_user)
    quoted_password = quote_plus(db_password)
    quoted_db_name = quote_plus(db_name)

    if db_password:
        credentials = f"{quoted_user}:{quoted_password}"
    else:
        credentials = quoted_user

    return (
        f"postgresql+psycopg2://{credentials}@{db_host}:{db_port}/{quoted_db_name}"
    )

class Settings:
    """Application settings loaded from environment variables."""
    database_url: str = _get_database_url()
    db_echo: bool = _get_bool("DB_ECHO", "false")
    secret_key: str = _get_required_env("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    cookie_secure: bool = _get_bool("COOKIE_SECURE", "true")
    frontend_origins: list[str] = _split_csv(
        os.getenv(
            "FRONTEND_ORIGINS",
            "https://localhost:5173,https://localhost:3000",
        )
    )
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "")
    smtp_use_tls: bool = _get_bool("SMTP_USE_TLS", "true")
    smtp_timeout_seconds: int = int(os.getenv("SMTP_TIMEOUT_SECONDS", "10"))
    verification_code_ttl_minutes: int = int(
        os.getenv("VERIFICATION_CODE_TTL_MINUTES", "10")
    )
    password_reset_token_ttl_minutes: int = int(
        os.getenv("PASSWORD_RESET_TOKEN_TTL_MINUTES", "30")
    )
    check_timeout_seconds: int = int(os.getenv("CHECK_TIMEOUT_SECONDS", "5"))
    check_execution_backend: str = os.getenv("CHECK_EXECUTION_BACKEND", "docker")
    check_docker_python_image: str = os.getenv(
        "CHECK_DOCKER_PYTHON_IMAGE",
        "legacy-trainer-python-runner:latest",
    )
    check_docker_cpp_image: str = os.getenv(
        "CHECK_DOCKER_CPP_IMAGE",
        "legacy-trainer-cpp-runner:latest",
    )
    check_docker_container_user: str = os.getenv(
        "CHECK_DOCKER_CONTAINER_USER",
        "65534:65534",
    )
    check_docker_workspace_dir: str = os.getenv(
        "CHECK_DOCKER_WORKSPACE_DIR",
        "/workspace",
    )
    check_workspace_root: str = os.getenv("CHECK_WORKSPACE_ROOT", "")
    check_docker_tmp_dir: str = os.getenv(
        "CHECK_DOCKER_TMP_DIR",
        "/tmp",
    )
    check_docker_memory_limit: str = os.getenv(
        "CHECK_DOCKER_MEMORY_LIMIT",
        "256m",
    )
    check_docker_cpus: str = os.getenv("CHECK_DOCKER_CPUS", "1.0")
    check_docker_pids_limit: int = int(os.getenv("CHECK_DOCKER_PIDS_LIMIT", "64"))
    check_docker_tmpfs_size: str = os.getenv(
        "CHECK_DOCKER_TMPFS_SIZE",
        "64m",
    )
    check_docker_disable_network: bool = _get_bool(
        "CHECK_DOCKER_DISABLE_NETWORK",
        "true",
    )
    check_docker_read_only_rootfs: bool = _get_bool(
        "CHECK_DOCKER_READ_ONLY_ROOTFS",
        "true",
    )
    check_docker_drop_capabilities: bool = _get_bool(
        "CHECK_DOCKER_DROP_CAPABILITIES",
        "true",
    )
    check_docker_no_new_privileges: bool = _get_bool(
        "CHECK_DOCKER_NO_NEW_PRIVILEGES",
        "true",
    )
    checker_sandbox_image: str = os.getenv(
        "CHECKER_SANDBOX_IMAGE",
        "legacy-trainer-checker:local",
    )
    checker_docker_bin: str = os.getenv("CHECKER_DOCKER_BIN", "docker")
    checker_sandbox_cpus: str = os.getenv("CHECKER_SANDBOX_CPUS", "0.5")
    checker_sandbox_memory: str = os.getenv("CHECKER_SANDBOX_MEMORY", "256m")
    checker_sandbox_pids_limit: int = int(
        os.getenv("CHECKER_SANDBOX_PIDS_LIMIT", "128")
    )
    checker_sandbox_user: str = os.getenv("CHECKER_SANDBOX_USER", "10001:10001")
    checker_sandbox_tmpfs_size: str = os.getenv(
        "CHECKER_SANDBOX_TMPFS_SIZE",
        "64m",
    )
    checker_sandbox_workspace_tmpfs_size: str = os.getenv(
        "CHECKER_SANDBOX_WORKSPACE_TMPFS_SIZE",
        "64m",
    )
    checker_sandbox_timeout_overhead_seconds: int = int(
        os.getenv("CHECKER_SANDBOX_TIMEOUT_OVERHEAD_SECONDS", "3")
    )
    checker_sandbox_cleanup_timeout_seconds: int = int(
        os.getenv("CHECKER_SANDBOX_CLEANUP_TIMEOUT_SECONDS", "5")
    )


settings = Settings()
