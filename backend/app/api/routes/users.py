import uuid
from typing import Any

from fastapi import APIRouter, Depends

from app import crud
from app.api.deps import (
    CurrentUser,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    MessageResponse,
    PasswordResetConfirm,
    User,
    UserCreate,
    UserPublic,
    UserCreate,
    UsersPublic,
    UserUpdate,
)
from app.utils import generate_new_account_email, send_email
from beanie.odm.fields import PydanticObjectId
from app.exceptions.auth_exceptions import AuthFail, PermissionDenied,SuperCanNotDeleteSelf
from app.exceptions.user_exceptions import IncorrectPassword, PasswordSame, UserNotFound,UserNotActive,UserExists

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
async def read_users(skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    # 获取用户总数
    count = await User.count()
    
    # 获取分页用户列表
    users = await User.find().skip(skip).limit(limit).to_list()
    users_public = []
    for user in users:
        try:
            user_pulic = user.to_public()
            users_public.append(user_pulic)
        except Exception as e:
            continue
    
    # return UserWithItems(data=users, count=count)
    return UsersPublic(data=users_public,count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
async def create_user(*, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = await crud.get_user_by_email(email=user_in.email)
    if user:
        raise UserNotFound

    user = await crud.create_user(user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch("/me", response_model=UserPublic)
async def update_user_me(
    *, user_in: UserUpdate, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """
    if user_in.email:
        existing_user = await crud.get_user_by_email(email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise UserExists
    
    user = await crud.update_user(db_user=current_user, user_in=user_in)
    return user


@router.patch("/me/password", response_model=MessageResponse)
async def update_password_me(
    *, body: PasswordResetConfirm, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise IncorrectPassword
    if body.current_password == body.new_password:
        raise PasswordSame
    
    current_user.hashed_password = get_password_hash(body.new_password)
    await current_user.save()
    return MessageResponse(MessageResponse="Password updated successfully")


@router.get("/me", response_model=UserPublic)
async def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=MessageResponse)
async def delete_user_me(current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise SuperCanNotDeleteSelf
    
    # 删除用户相关的所有项目
    await Item.find(Item.owner == current_user).delete()
    await current_user.delete()
    return MessageResponse(detail="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
async def register_user(user_in: UserCreate) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = await crud.get_user_by_email(email=user_in.email)
    if user:
        raise UserExists
    user_create = UserCreate.model_validate(user_in)
    user = await crud.create_user(user_create=user_create)
    return user


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: uuid.UUID, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = await User.get(user_id)
    if not user:
        raise UserNotFound
    if user.id == current_user.id:
        return user
    if not current_user.is_superuser:
        raise PermissionDenied
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
async def update_user(
    *,
    user_id: PydanticObjectId,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    db_user = await User.get(user_id)
    if not db_user:
        raise UserNotFound
    
    if user_in.email:
        existing_user = await crud.get_user_by_email(email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise UserExists

    db_user = await crud.update_user(db_user=db_user, user_in=user_in)
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
async def delete_user(
    current_user: CurrentUser, user_id: PydanticObjectId
) -> MessageResponse:
    """
    Delete a user.
    """
    user = await User.get(user_id)
    if not user:
        raise UserNotFound
    if user.id == current_user.id:
        raise SuperCanNotDeleteSelf
    
    # 删除用户相关的所有项目
    await Item.find(Item.owner == user).delete()
    await user.delete()
    return MessageResponse(detail="User deleted successfully")
