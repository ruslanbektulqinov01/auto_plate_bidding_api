from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.controllers.plate_controller import PlateController
from app.database import get_session as get_db
from app.models.user import User
from app.schemas.plate import Plate, PlateCreate, PlateUpdate

router = APIRouter(prefix="/plates", tags=["plates"])


@router.get("/", response_model=List[Plate])
async def get_plates(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    Get all plates.
    """
    plate_controller = PlateController(db)
    return await plate_controller.get_plates(skip, limit)


@router.get("/{plate_id}", response_model=Plate)
async def get_plate(
        plate_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific plate by ID.
    """
    plate_controller = PlateController(db)
    plate = await plate_controller.get_plate(plate_id)
    if not plate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plate not found"
        )
    return plate


@router.post("/", response_model=Plate, status_code=status.HTTP_201_CREATED)
async def create_plate(
        plate_in: PlateCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    Create a new plate.
    """
    # Check if user has admin privileges
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create plates"
        )

    plate_controller = PlateController(db)
    # Ensure the type is correctly passed to the controller
    return await plate_controller.create_plate(plate_in)


@router.put("/{plate_id}", response_model=Plate)
async def update_plate(
        plate_id: int,
        plate_in: PlateUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    Update a plate.
    """
    # Check if user has admin privileges
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update plates"
        )

    plate_controller = PlateController(db)
    plate = await plate_controller.get_plate(plate_id)
    if not plate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plate not found"
        )

    updated_plate = await plate_controller.update_plate(plate_id, plate_in)
    return updated_plate


@router.delete("/{plate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plate(
        plate_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """
    Delete a plate.
    """
    # Check if user has admin privileges
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete plates"
        )

    plate_controller = PlateController(db)
    plate = await plate_controller.get_plate(plate_id)
    if not plate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plate not found"
        )

    await plate_controller.delete_plate(plate_id)
    return None