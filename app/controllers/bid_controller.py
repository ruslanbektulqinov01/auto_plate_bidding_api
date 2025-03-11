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
    def __init__(self,
                 session: AsyncSession = Depends(get_session),
                    plate_controller: PlateController = Depends(),
                    user_controller: UserController = Depends()
                 ):
        self.__session: AsyncSession = session
        self.__plate_controller = plate_controller
        self.__user_controller = user_controller


    async def create_bid(self, data: BidCreate) -> Bid:
        """
        Create a new bid
        """
        # Check if plate exists and is active
        plate = await self.__plate_controller.get_plate(data.plate_id)
        if not plate or not plate.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plate not found or bidding is not active"
            )

        # Check if user exists
        user = await self.__session.get(User, data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if bid amount is higher than current highest bid
        highest_bid = plate.get_highest_bid()
        if highest_bid and data.amount <= highest_bid.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bid amount must be higher than current highest bid: {highest_bid.amount}"
            )

        bid = Bid(
            user_id=data.user_id,
            plate_id=data.plate_id,
            amount=data.amount,
            is_active=True
        )
        self.__session.add(bid)
        await self.__session.commit()
        await self.__session.refresh(bid)
        return bid

    async def get_bid(self, bid_id: int) -> Optional[Bid]:
        """
        Get a bid by ID
        """
        return await self.__session.get(Bid, bid_id)

    async def list_bids(self, skip: int = 0, limit: int = 100) -> Sequence[Bid]:
        """
        Get all bids
        """
        bids = await self.__session.execute(select(Bid).offset(skip).limit(limit))
        return bids.scalars().all()

    async def get_bids_by_user(self, user_id: int) -> Sequence[Bid]:
        """
        Get all bids placed by a specific user
        """
        user = await self.__session.get(User, user_id)
        return user.bids

    async def get_bids_by_plate(self, plate_id: int) -> Sequence[Bid]:
        """
        Get all bids for a specific plate
        """
        plate = await self.__session.get(AutoPlate, plate_id)
        return plate.bids

    async def update_bid(self, bid_id: int, data: BidUpdate) -> Optional[Bid]:
        """
        Update a bid
        """
        bid = await self.get_bid(bid_id)
        if not bid:
            return None

        # Check if bid can be updated
        plate = await self.__plate_controller.get_plate(bid.plate_id)
        if not plate or not plate.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update bid for inactive plate"
            )

        for field, value in data.model_dump(exclude_unset=True).items():
            # If updating amount, check if it's higher than current highest bid
            if field == "amount" and value is not None:
                highest_bid = plate.get_highest_bid()
                if highest_bid and highest_bid.id != bid_id and value <= highest_bid.amount:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Bid amount must be higher than current highest bid: {highest_bid.amount}"
                    )
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

    async def get_active_bids_by_user(self, user_id: int) -> List[Bid]:
        """
        Get all active bids for a user
        """
        user = await self.__user_controller.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user.get_active_bids()

    async def get_highest_bid_for_plate(self, plate_id: int) -> Optional[Bid]:
        """
        Get the highest bid for a plate
        """
        plate = await self.__plate_controller.get_plate(plate_id)
        if not plate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plate not found"
            )

        return plate.get_highest_bid()