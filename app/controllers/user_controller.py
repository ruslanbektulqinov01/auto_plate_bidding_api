from typing import Optional, Sequence
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, User


class UserController:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def create_user(self, data: UserCreate) -> User:
        # Create a new user based UserCreate schema
        user = User(
            username=data.username,
            email=data.email,
            hashed_password=data.password,
            is_staff=data.is_staff,
        )
        self.__session.add(user)
        await self.__session.commit()
        await self.__session.refresh(user)
        return user

    async def get_user(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID
        """
        return await self.__session.get(User, user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email
        """
        return await self.__session.get(User, email)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username
        """
        return await self.__session.get(User, username)

    async def list_users(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """
        Get all users
        """
        users = await self.__session.execute(select(User).offset(skip).limit(limit))
        return users.scalars().all()

    async def update_user(self, user_id: int, data: UserUpdate) -> Optional[User]:
        """
        Update a user
        """
        user = await self.get_user(user_id)
        if not user:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            # Handle password separately to hash it
            if field == "password" and value is not None:
                setattr(
                    user, "hashed_password", value
                )  # In actual implementation, hash this password
            elif field != "password":
                setattr(user, field, value)

        user.updated_at = datetime.now()
        await self.__session.commit()
        await self.__session.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> bool:
        """
        Delete a user
        """
        user = await self.get_user(user_id)
        if not user:
            return False

        await self.__session.delete(user)
        await self.__session.commit()
        return True

    async def activate_user(self, user_id: int) -> Optional[User]:
        """
        Activate a user account
        """
        user = await self.get_user(user_id)
        if not user:
            return None

        user.is_active = True
        await self.__session.commit()
        await self.__session.refresh(user)
        return user

    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """
        Deactivate a user account
        """
        user = await self.get_user(user_id)
        if not user:
            return None

        user.is_active = False
        await self.__session.commit()
        await self.__session.refresh(user)
        return user
