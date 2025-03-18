from typing import Optional, Sequence, List
from fastapi import Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import get_session
from app.models.bid import Bid
from app.models.user import User
from app.models.plate import AutoPlate
from app.schemas.bid import BidCreate, BidUpdate
from app.controllers.plate_controller import PlateController
from app.controllers.user_controller import UserController


class BidController:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
    ):
        self.__session: AsyncSession = session

    async def create_bid(self, data: BidCreate, current_user) -> Bid:
        """
        Create a new bid
        """
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Check if plate exists and is active
        plate = await self.__session.get(AutoPlate, data.plate_id)
        if not plate or not plate.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot place bid for inactive plate",
            )

        # Check if user already has a bid for this plate
        query = select(Bid).where(
            Bid.user_id == current_user.id,
            Bid.plate_id == data.plate_id
        )
        result = await self.__session.execute(query)
        existing_bid = result.scalar_one_or_none()

        if existing_bid:
            # Update existing bid
            existing_bid.amount = data.amount
            existing_bid.updated_at = datetime.now()
            bid = existing_bid
        else:
            # Create new bid
            bid = Bid(**data.model_dump())
        bid.user_id = current_user.id
        self.__session.add(bid)

        # Update plate price if new bid is higher
        if plate.price < data.amount:
            plate.price = data.amount
            plate.updated_at = datetime.now()

        await self.__session.commit()
        await self.__session.refresh(bid)
        return bid

    async def get_bid(self, bid_id: int) -> Optional[Bid]:
        """
        Get a bid by ID
        """
        return await self.__session.get(Bid, bid_id)

    # async def get_bids(self, skip: int = 0, limit: int = 100, current_user) -> Sequence[Bid]:
    #     """
    #     Get all bids
    #     """
    #     if not current_user:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
    #         )
    #     query = select(Bid).offset(skip).limit(limit)
    #     result = await self.__session.execute(query)
    #     return result.scalars().all()

    async def get_bids_by_user(self, user_id: int) -> Sequence[Bid]:
        user = await self.__session.get(User, user_id)
        bids = select(Bid).where(Bid.user_id == user_id)
        result = await self.__session.execute(bids)
        return result.scalars().all()

    async def get_bids_by_plate(self, plate_id: int) -> Sequence[Bid]:
        """
        Get all bids for a specific plate
        """
        plate = await self.__session.get(AutoPlate, plate_id)
        return plate.bids

    async def update_bid(self, bid_id: int, data: BidUpdate, current_user) -> Optional[Bid]:
        """
        Update a bid
        """
        if not current_user and not current_user.is_staff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data"
            )

        bid = await self.get_bid(bid_id)
        if not bid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Bid not found"
            )
        # Update plate price if new bid is higher
        plate = await self.__session.get(AutoPlate, bid.plate_id)
        if plate.price < data.amount:
            plate.price = data.amount
            plate.updated_at = datetime.now()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bid amount must be higher than current price",
            )

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(bid, field, value)
        bid.updated_at = datetime.now()
        await self.__session.commit()
        await self.__session.refresh(bid)
        return bid

    async def delete_bid(self, bid_id: int) -> bool:
        """
        Delete a bid
        """
        bid = await self.get_bid(bid_id)
        if not bid:
            return False

        await self.__session.delete(bid)
        await self.__session.commit()
        return True


    async def get_highest_bid_for_plate(self, plate_id: int) -> Optional[Bid]:
        """
        Get the highest bid for a plate
        """
        plate = await self.__session.get(AutoPlate, plate_id)
        if not plate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Plate not found"
            )

        query = select(Bid).where(Bid.plate_id == plate_id).order_by(Bid.amount.desc())
        result = await self.__session.execute(query)
        return result.scalar_one_or_none()
