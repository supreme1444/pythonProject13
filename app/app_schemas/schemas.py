from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    user: str
    hashed_password: str
    referral_code: str = ""


class UserResponse(UserBase):
    user: str
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReferralCodeResponse(BaseModel):
    code: str
    expiration_date: datetime

    class Config:
        from_attributes = True



class ReferralResponse(BaseModel):
    referral_id: int
    created_at: datetime

    class Config:
        from_attributes = True
