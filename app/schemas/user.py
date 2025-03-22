from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base schema with common user attributes"""

    email: str
    username: Optional[str] = None
    is_staff: Optional[bool] = False


class UserCreate(UserBase):
    """Schema for creating a new user"""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating user information"""

    email: str
    username: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDBBase(UserBase):
    """Base schema for users stored in DB"""

    id: int

    class Config:
        from_attributes = True


class UserSchema(UserInDBBase):
    """Schema for public user data (returned to clients)"""

    pass


class UserInDB(UserInDBBase):
    """Schema for user data stored in DB (includes hashed password)"""

    hashed_password: str


class UserResponse(UserBase):
    """Schema for user response data"""

    id: int


# user login wiht username and password
class UserLogin(BaseModel):
    username: str
    password: str
