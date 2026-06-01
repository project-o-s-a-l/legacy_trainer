from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.app.db.enums import VerificationFlow


class RequestVerificationCodeRequest(BaseModel):
    email: EmailStr
    flow: VerificationFlow


class RequestVerificationCodeResponse(BaseModel):
    message: str = "Verification code sent successfully"

class VerifyVerificationCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=6)
    flow: VerificationFlow

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        code = value.strip()
        if not code.isdigit() or not 4 <= len(code) <= 6:
            raise ValueError("Code must contain 4 to 6 digits")
        return code


class VerifyVerificationCodeResponse(BaseModel):
    message: str
    resetToken: str | None = None