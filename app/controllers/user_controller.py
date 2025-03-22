from typing import Optional, Sequence
from fastapi import Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.core.security import get_password_hash
from app.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserController:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.__session: AsyncSession = session

    async def create_user(self, data: UserCreate) -> User:
        """Create a new user based on UserCreate schema"""
        try:
            # Check if username exists
            if await self.get_user_by_username(data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists",
                )

                # Check if email exists
            if await self.get_user_by_email(data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists",
                )

            # Create user object without password field
            user_data = data.model_dump(exclude={"password"})
            user = User(**user_data)

            # Hash password separately to avoid passlib issues
            user.hashed_password = get_password_hash(data.password)
            self.__session.add(user)
            await self.__session.commit()
            await self.__session.refresh(user)
            return user
        except Exception as e:
            await self.__session.rollback()
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating user: {str(e)}",
            )

    async def get_user(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID
        """
        return await self.__session.get(User, user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email
        """
        result = await self.__session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username
        """
        result = await self.__session.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()

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
                setattr(user, "hashed_password", get_password_hash(value))
            elif field != "password":
                setattr(user, field, value)

        # Check if the User model has updated_at field
        if hasattr(user, "updated_at"):
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
