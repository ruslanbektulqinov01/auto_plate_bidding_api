from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.controllers.bid_controller import BidController
from app.controllers.plate_controller import PlateController
from app.database import get_session as get_db
from app.models.user import User
from app.schemas.bid import Bid, BidCreate, BidUpdate

router = APIRouter(prefix="/bids", tags=["bids"])


@router.get("/", response_model=List[Bid])
async def get_bids(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all bids with optional filtering by plate_id or user_id.
    """
    bid_controller = BidController(db)
    return await bid_controller.get_bids(skip, limit)


@router.get("/{bid_id}", response_model=Bid)
async def get_bid(
    bid_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific bid by ID.
    """
    bid_controller = BidController(db)
    bid = await bid_controller.get_bid(bid_id)
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bid not found"
        )
    return bid


@router.post("/", response_model=Bid, status_code=status.HTTP_201_CREATED)
async def create_bid(
    bid_in: BidCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Place a new bid.
    """
    bid_controller = BidController(db)
    plate_controller = PlateController(db)

    # Check if plate exists
    plate = await plate_controller.get_plate(bid_in.plate_id)
    if not plate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plate not found"
        )

    # Check if the plate is active for bidding
    if not plate.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This plate is not available for bidding",
        )

    # Set the user ID from the current user
    bid_data = bid_in.model_dump()
    bid_data["user_id"] = current_user.id

    # Create bid with user ID
    new_bid = BidCreate(**bid_data)
    return await bid_controller.create_bid(new_bid)


@router.put("/{bid_id}", response_model=Bid)
async def update_bid(
    bid_id: int,
    bid_in: BidUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a bid.
    """
    bid_controller = BidController(db)
    bid = await bid_controller.get_bid(bid_id)

    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bid not found"
        )

    # Check if the user owns this bid or is admin
    if bid.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this bid",
        )

    updated_bid = await bid_controller.update_bid(bid_id, bid_in)
    return updated_bid


@router.delete("/{bid_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bid(
    bid_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a bid.
    """
    bid_controller = BidController(db)
    bid = await bid_controller.get_bid(bid_id)

    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bid not found"
        )

    # Check if the user owns this bid or is admin
    if bid.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this bid",
        )

    await bid_controller.delete_bid(bid_id)
    return None


@router.get("/plates/{plate_id}/highest", response_model=Bid)
async def get_highest_bid(
    plate_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the highest bid for a specific plate.
    """
    plate_controller = PlateController(db)
    try:
        highest_bid = await plate_controller.get_highest_bid_for_plate(plate_id)
        if not highest_bid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No bids found for this plate",
            )
        return highest_bid
    except HTTPException:
        raise
