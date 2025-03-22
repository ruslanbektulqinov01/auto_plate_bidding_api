from typing import Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BidBase(BaseModel):
    """Base schema with common bid attributes"""

    amount: float = Field(..., description="Amount of the bid", gt=0)
    is_active: bool = Field(True, description="Whether the bid is currently active")


class BidCreate(BidBase):
    plate_id: int


class BidUpdate(BaseModel):
    """Schema for updating bid information"""

    amount: Optional[float] = Field(None, description="Amount of the bid", gt=0)


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

    plate: Any
    user: Any
