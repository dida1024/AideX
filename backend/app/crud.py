from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate
from beanie import PydanticObjectId

async def create_user(*, user_create: UserCreate) -> User:
    user_data = user_create.model_dump()
    user_data["hashed_password"] = get_password_hash(user_create.password)
    db_obj = User.model_validate(user_data)
    await db_obj.insert()
    return db_obj

async def update_user(*, db_user: User, user_in: UserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    await db_user.save()
    return db_user

async def get_user_by_email(*, email: str) -> User | None:
    return await User.find_one({"email": email})

async def authenticate(*, email: str, password: str) -> User | None:
    db_user = await get_user_by_email(email=email)
    if not db_user:
        # TODO： raise better error
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user

async def create_item(*, item_in: ItemCreate, owner_id: PydanticObjectId) -> Item:
    item_data = item_in.model_dump()
    item_data["owner_id"] = owner_id
    db_item = Item.model_validate(item_data)
    await db_item.insert()
    return db_item
