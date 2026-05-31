from pydantic import BaseModel, EmailStr

from backend.app.db.enums import VerificationFlow


class RequestVerificationCodeRequest(BaseModel):
    email: EmailStr
    flow: VerificationFlow


class RequestVerificationCodeResponse(BaseModel):
    message: str = "Verification code sent successfully"