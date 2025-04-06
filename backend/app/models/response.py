from typing import List, TypeVar, Generic, Optional, Any
from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel

# 定义泛型类型变量
T = TypeVar('T')

class PaginatedResults(BaseModel):
    total: int
    results: List[BaseModel]

# 通用API响应模型
class ApiResponse(GenericModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool = True
    code: int = 200
    message: str = "操作成功"
    data: Optional[T] = None
    meta: Optional[dict] = None
    
    @classmethod
    def success_response(cls, data: T = None, message: str = "操作成功", code: int = 200, meta: dict = None) -> "ApiResponse[T]":
        """创建成功响应"""
        return cls(
            success=True,
            code=code,
            message=message,
            data=data,
            meta=meta
        )
    
    @classmethod
    def error_response(cls, message: str = "操作失败", code: int = 400, data: Any = None) -> "ApiResponse[T]":
        """创建错误响应"""
        return cls(
            success=False,
            code=code,
            message=message,
            data=data
        )

# 分页数据响应包装器
class PaginatedResponse(ApiResponse, Generic[T]):
    data: List[T]
    meta: dict = {"total": 0, "page": 1, "page_size": 10}
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int = 1, page_size: int = 10) -> "PaginatedResponse[T]":
        """创建分页响应"""
        return cls(
            data=items, 
            meta={
                "total": total,
                "page": page,
                "page_size": page_size
            }
        )

# 保留兼容性
class MessageResponse(BaseModel):
    detail: str 