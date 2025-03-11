from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """
    Schema for the token response that will be returned to users
    """
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    Schema representing the payload of JWT token
    """
    sub: Optional[str] = None
    exp: Optional[int] = None


class TokenData(BaseModel):
    """
    Schema containing user information extracted from token
    """
    user_id: Optional[str] = None