from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field
from beanie import Document, Link, Indexed, PydanticObjectId
from beanie.odm.fields import WriteRules

# ------------------------ 基础模型 ------------------------
class TimestampMixin(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# ------------------------ 用户模型 ------------------------
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

# ------------------------ 项目模型 ------------------------
class ItemBase(TimestampMixin):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=512)
    is_public: bool = Field(default=True, index=True)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=512)
    is_public: Optional[bool] = None

class Item(ItemBase, Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    owner: Link[User] = Field(
        default=None,
        description="Owner of the item",
    )

    class Settings:
        name = "items"
        use_state_management = True

    async def to_public(self) -> "ItemPublic":
        """转换为公共项目模型"""
        owner = await self.owner.fetch() if isinstance(self.owner, Link) else self.owner
        if not owner:
            raise ValueError("Owner not found")

        return ItemPublic(
            id=self.id,
            title=self.title,
            description=self.description,
            is_public=self.is_public,
            created_at=self.created_at,
            updated_at=self.updated_at,
            owner=owner.to_public(),
        )

class ItemPublic(ItemBase):
    id: PydanticObjectId = Field(alias="id")
    owner: UserPublic

    @classmethod
    async def from_item(cls, item: Item) -> "ItemPublic":
        """从项目创建公共项目模型"""
        return await item.to_public()

class ItemsPublic(BaseModel):
    data: list[ItemPublic]
    count: int

# ------------------------ 认证模型 ------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: str | None = None
    exp: datetime | None = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=40)

# ------------------------ 响应模型 ------------------------
class PaginatedResults(BaseModel):
    total: int
    results: List[BaseModel]

class MessageResponse(BaseModel):
    detail: str

# ------------------------ 关系处理 ------------------------
User.model_rebuild()
Item.model_rebuild()