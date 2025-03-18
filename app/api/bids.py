from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user, get_current_user
from app.controllers.bid_controller import BidController
from app.controllers.plate_controller import PlateController
from app.database import get_session as get_db
from app.models.user import User
from app.schemas.bid import Bid, BidCreate, BidUpdate

router = APIRouter(prefix="/bids", tags=["bids"])


@router.get("/", response_model=List[Bid],
            status_code=status.HTTP_200_OK,
            description="Get all bids",
            summary="Get all bids",
            )
async def get_bids_by_user(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    bid_controller = BidController(db)
    return await bid_controller.get_bids_by_user(current_user.id)


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


@router.post("/", response_model=Bid,
             status_code=status.HTTP_201_CREATED,
             description="Create a new bid",
             summary="Create a new bid",
             )
async def create_bid(
        bid_in: BidCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    bid_controller = BidController(db)
    bid_data = bid_in.model_dump()
    new_bid = BidCreate(**bid_data)
    return await bid_controller.create_bid(new_bid, current_user)


@router.put("/{bid_id}", response_model=Bid,
            status_code=status.HTTP_200_OK,
            description="Update a bid",
            summary="Update a bid",
            )
async def update_bid(
        bid_id: int,
        bid_in: BidUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    bid_controller = BidController(db)
    # bid = await bid_controller.get_bid(bid_id)
    #
    # if not bid:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND, detail="Bid not found"
    #     )
    #
    # # Check if the user owns this bid or is admin
    # if bid.user_id != current_user.id and not current_user.is_staff:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not enough permissions to update this bid",
    #     )

    updated_bid = await bid_controller.update_bid(bid_id, bid_in, current_user)
    return updated_bid


@router.delete("/{bid_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bid(
        bid_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
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
    if bid.user_id != current_user.id and not current_user.is_staff:
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
