from sqlalchemy import select

from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from pydantic import ValidationError, BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.user import User
from app.schemas.token import TokenData
from app.core.config import settings

# Security configurations
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)


async def authenticate_user(
    username: str, password: str, session: AsyncSession
) -> Union[User, None]:
    user = await session.execute(select(User).where(User.username == username))
    user = user.scalars().first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await session.execute(
        select(User).where(User.username == token_data.username)
    )
    user = user.scalars().first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> bool:
    """
    Get the current user's staff status
    """
    return current_user.is_staff


class TokenPayload(BaseModel):
    sub: str
    exp: int


# Add this function to retrieve a user by ID
async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get a user by ID
    """
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


# Fix the WebSocket authentication function
async def get_current_user_ws(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    try:
        token = websocket.query_params.get("token")
        if not token:
            # Optional: Close connection for unauthenticated users
            # await websocket.close(code=1008, reason="Not authenticated")
            return None

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None

        # Get user by username instead of ID
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalars().first()

        if not user:
            # Optional: Close connection for invalid users
            # await websocket.close(code=1008, reason="User not found")
            return None

        return user
    except (JWTError, ValidationError):
        # Optional: Close connection for invalid tokens
        # await websocket.close(code=1008, reason="Invalid token")
        return None
