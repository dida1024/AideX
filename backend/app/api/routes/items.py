from typing import Any
import logging

from fastapi import APIRouter
from beanie.odm.fields import PydanticObjectId

from app.api.deps import CurrentUser
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, MessageResponse, UserPublic
from app.models.response import ApiResponse, PaginatedResponse
from app.exceptions.auth_exceptions import PermissionDenied
from app.exceptions.item_exceptions import ItemNotFound


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ApiResponse[list[ItemPublic]])
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
    
    # 返回分页响应
    return PaginatedResponse.create(
        items=items_public,
        total=count,
        page=skip // limit + 1 if limit else 1,
        page_size=limit
    )


@router.get("/{id}", response_model=ApiResponse[ItemPublic])
async def read_item(current_user: CurrentUser, id: PydanticObjectId) -> Any:
    """
    Get item by ID.
    """
    item = await Item.get(id)
    if not item:
        raise ItemNotFound
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise PermissionDenied
    
    item_public = await ItemPublic.from_item(item)
    return ApiResponse.success_response(data=item_public)


@router.post("/", response_model=ApiResponse[ItemPublic])
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
    
    item_public = await ItemPublic.from_item(item)
    return ApiResponse.success_response(
        data=item_public,
        message="项目创建成功",
        code=201
    )


@router.put("/{id}", response_model=ApiResponse[ItemPublic])
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
    item_public = await ItemPublic.from_item(item)
    return ApiResponse.success_response(
        data=item_public,
        message="项目更新成功"
    )


@router.delete("/{id}", response_model=ApiResponse[None])
async def delete_item(
    current_user: CurrentUser, id: PydanticObjectId
) -> Any:
    """
    Delete an item.
    """
    item = await Item.get(id)
    if not item:
        raise ItemNotFound
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise PermissionDenied
    
    await item.delete()
    return ApiResponse.success_response(message="项目删除成功")
