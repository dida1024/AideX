from typing import Any
import logging

from fastapi import APIRouter
from beanie.odm.fields import PydanticObjectId

from app.api.deps import CurrentUser
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, MessageResponse, UserPublic
from app.exceptions.auth_exceptions import PermissionDenied
from app.exceptions.item_exceptions import ItemNotFound


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
async def read_items(
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve items.
    """
    # 获取项目总数
    count = await Item.count()
    
    # 获取分页项目列表
    items = await Item.find().skip(skip).limit(limit).to_list()
    
    # 将 Item 转换为 ItemPublic
    items_public = []
    for item in items:
        try:
            item_public = await ItemPublic.from_item(item)
            items_public.append(item_public)
        except Exception as e:
            logger.error(f"Error processing item {item.id}: {str(e)}")
            continue
    
    return ItemsPublic(data=items_public, count=count)


@router.get("/{id}", response_model=ItemPublic)
async def read_item(current_user: CurrentUser, id: PydanticObjectId) -> Any:
    """
    Get item by ID.
    """
    item = await Item.get(id)
    if not item:
        raise ItemNotFound
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise PermissionDenied
    
    return await ItemPublic.from_item(item)


@router.post("/", response_model=ItemPublic)
async def create_item(
    *, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item_data = item_in.model_dump()
    item_data["owner"] = current_user
    item = Item.model_validate(item_data)
    await item.insert()
    
    return await ItemPublic.from_item(item)


@router.put("/{id}", response_model=ItemPublic)
async def update_item(
    *,
    current_user: CurrentUser,
    id: PydanticObjectId,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    item = await Item.get(id)
    if not item:
        raise ItemNotFound
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise PermissionDenied
    
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await item.save()
    return await ItemPublic.from_item(item)


@router.delete("/{id}")
async def delete_item(
    current_user: CurrentUser, id: PydanticObjectId
) -> MessageResponse:
    """
    Delete an item.
    """
    item = await Item.get(id)
    if not item:
        raise ItemNotFound
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise PermissionDenied
    
    await item.delete()
    return MessageResponse(detail="Item deleted successfully")
