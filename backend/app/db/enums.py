import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class TaskDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TaskStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


class SubmissionCheckType(str, enum.Enum):
    TESTS = "tests"
    LINT = "lint"
    STATIC = "static"
    ARCHITECTURE = "architecture"


class CheckStatus(str, enum.Enum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"

class VerificationFlow(str, enum.Enum):
    REGISTRATION = "registration"
    RECOVERY = "recovery"