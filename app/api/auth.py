from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.controllers.user_controller import UserController
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from app.schemas.token import Token

# Constants for token expiration
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create router instance
auth_router = APIRouter(tags=["Authentication"])


@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_controller: UserController = Depends(),
):
    """
    Authenticate user and generate JWT token
    """
    user = await authenticate_user(
        user_controller, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    user_controller: UserController = Depends(),
):
    # Your existing code remains the same
    new_user = await user_controller.create_user(user_data)
    return new_user  # FastAPI converts this to UserResponse automatically


@auth_router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get information about the currently authenticated user
    """
    return current_user
