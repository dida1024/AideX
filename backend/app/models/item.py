from typing import Optional
from pydantic import BaseModel, Field
from beanie import Document, Link, PydanticObjectId

from app.models.base import TimestampMixin
from app.models.user import User, UserPublic

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
    owner: Link["User"] = Field(
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