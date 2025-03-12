from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PlateBase(BaseModel):
    """Base schema with common plate attributes"""

    description: Optional[str] = Field(None, description="Description of the plate")
    price: float = Field(..., description="Price of the plate", gt=0)
    is_active: bool = Field(
        True, description="Whether the plate is currently available"
    )


class PlateCreate(PlateBase):
    """Schema for creating a new plate"""

    plate_number: str
    deadline: datetime


class PlateUpdate(BaseModel):
    """Schema for updating plate information"""

    name: Optional[str] = Field(None, description="Name of the plate")
    description: Optional[str] = Field(None, description="Description of the plate")
    price: Optional[float] = Field(None, description="Price of the plate", gt=0)
    is_active: Optional[bool] = Field(
        None, description="Whether the plate is currently available"
    )


class PlateInDBBase(PlateBase):
    """Base schema for plates stored in DB"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Plate(PlateInDBBase):
    """Schema for public plate data (returned to clients)"""

    pass


class PlateInDB(PlateInDBBase):
    """Schema for plate data stored in DB"""

    pass


class PlateWithCategory(Plate):
    """Schema for plate data with its category information"""

    category: Any  # This will be replaced with the actual Category model
