from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.core.security import get_password_hash
from app.models import (
    User,
    UserPublic,
)

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    is_verified: bool = False


@router.post("/users/", response_model=UserPublic)
async def create_user(user_in: PrivateUserCreate) -> Any:
    """
    Create a new user.
    """
    # 检查邮箱是否已存在
    existing_user = await User.find_one(User.email == user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    # 创建用户数据
    user_data = {
        "email": user_in.email,
        "full_name": user_in.full_name,
        "hashed_password": get_password_hash(user_in.password),
        "is_verified": user_in.is_verified,
    }
    
    try:
        user = User.model_validate(user_data)
        await user.insert()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the user.",
        )

    return user
