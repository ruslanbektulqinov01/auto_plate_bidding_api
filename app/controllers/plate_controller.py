from typing import Optional, Sequence
from fastapi import Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import get_session
from app.models.plate import AutoPlate
from app.schemas.plate import PlateCreate, PlateUpdate


class PlateController:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def create_plate(self, data: PlateCreate, user) -> AutoPlate:
        """
        Create a new auto plate
        """
        # with model_dump
        plate = AutoPlate(**data.model_dump())
        plate.created_by_id = user.id
        self.__session.add(plate)
        await self.__session.commit()
        await self.__session.refresh(plate)
        return plate

    async def get_plate(self, plate_id: int) -> Optional[AutoPlate]:
        """
        Get a plate by ID
        """
        if not await self.__session.get(AutoPlate, plate_id):
            return None
        return await self.__session.get(AutoPlate, plate_id)

    async def get_plate_by_number(self, plate_number: str) -> Optional[AutoPlate]:
        """
        Get a plate by plate number
        """
        return await self.__session.get(AutoPlate, plate_number)

    async def get_plate_by_id(self, plate_id: int) -> Optional[AutoPlate]:
        """
        Get a plate by ID
        """
        return await self.__session.get(AutoPlate, plate_id)

    async def get_plates(self, skip: int = 0, limit: int = 100) -> Sequence[AutoPlate]:
        """
        Get all plates
        """
        plates = await self.__session.execute(
            select(AutoPlate).offset(skip).limit(limit)
        )
        return plates.scalars().all()

    async def update_plate(
        self, plate_id: int, data: PlateUpdate
    ) -> Optional[AutoPlate]:
        """
        Update a plate
        """
        plate = await self.get_plate(plate_id)
        if not plate:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(plate, field, value)
        plate.updated_at = datetime.now()
        await self.__session.commit()
        await self.__session.refresh(plate)
        return plate

    async def delete_plate(self, plate_id: int) -> bool:
        """
        Delete a plate
        """
        plate = await self.get_plate(plate_id)
        if not plate:
            return False

        await self.__session.delete(plate)
        await self.__session.commit()
        return True

    async def get_highest_bid_for_plate(self, plate_id: int):
        """
        Get the highest bid for a plate
        """
        from sqlalchemy import select, desc
        from app.models.bid import Bid

        # Fetch the highest bid directly with a proper query
        result = await self.__session.execute(
            select(Bid)
            .where(Bid.plate_id == plate_id)
            .order_by(desc(Bid.amount))
            .limit(1)
        )
        return result.scalar_one_or_none()
