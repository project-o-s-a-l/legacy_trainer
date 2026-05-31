from pydantic import BaseModel, EmailStr, Field

from backend.app.schemas.user import UserShortResponse


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=35)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RegisterResponse(BaseModel):
    message: str = "Verification code sent successfully"
    email: EmailStr


class LoginRequest(BaseModel):
    login: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LoginUserResponse(BaseModel):
    id: int
    login: str


class LoginResponse(BaseModel):
    token: str
    user: LoginUserResponse


class MessageResponse(BaseModel):
    message: str
