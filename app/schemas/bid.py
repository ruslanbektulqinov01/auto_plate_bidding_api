from typing import Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BidBase(BaseModel):
    """Base schema with common bid attributes"""
    amount: float = Field(..., description="Amount of the bid", gt=0)
    plate_id: int = Field(..., description="ID of the plate this bid is for")
    user_id: int = Field(..., description="ID of the user placing the bid")
    description: Optional[str] = Field(None, description="Additional notes about the bid")
    is_active: bool = Field(True, description="Whether the bid is currently active")
    expiration_date: Optional[datetime] = Field(None, description="When the bid expires")


class BidCreate(BidBase):
    """Schema for creating a new bid"""
    pass


class BidUpdate(BaseModel):
    """Schema for updating bid information"""
    amount: Optional[float] = Field(None, description="Amount of the bid", gt=0)
    description: Optional[str] = Field(None, description="Additional notes about the bid")
    is_active: Optional[bool] = Field(None, description="Whether the bid is currently active")
    expiration_date: Optional[datetime] = Field(None, description="When the bid expires")


class BidInDBBase(BidBase):
    """Base schema for bids stored in DB"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Bid(BidInDBBase):
    """Schema for public bid data (returned to clients)"""
    pass


class BidInDB(BidInDBBase):
    """Schema for bid data stored in DB"""
    pass


class BidWithDetails(Bid):
    """Schema for bid data with plate and user information"""
    plate: Any  # This will be replaced with the actual Plate model
    user: Any   # This will be replaced with the actual User model