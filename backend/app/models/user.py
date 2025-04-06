from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from beanie import Document, Link, PydanticObjectId

from app.models.base import TimestampMixin

class UserBase(TimestampMixin):
    email: Optional[EmailStr] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: bool = Field(default=True, index=True)
    is_superuser: bool = Field(default=False)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=40)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

class User(UserBase, Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    hashed_password: str
    last_login: Optional[datetime] = None

    class Settings:
        name = "users"
        use_state_management = True

    def to_public(self) -> "UserPublic":
        """转换为公共用户模型"""
        return UserPublic(
            id=self.id,
            email=self.email,
            full_name=self.full_name,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
        )

class UserPublic(UserBase):
    id: PydanticObjectId = Field(alias="id")

class UsersPublic(BaseModel):
    data: list[UserPublic]
    count: int

class UserWithItems(UserPublic):
    items: List["ItemPublic"] = []

# 为避免循环导入，在文件末尾导入
from app.models.item import ItemPublic 