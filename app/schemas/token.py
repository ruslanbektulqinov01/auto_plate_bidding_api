from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """
    Schema for token response
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for token payload data
    """
    username: Optional[str] = None