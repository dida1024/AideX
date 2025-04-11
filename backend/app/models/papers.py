from typing import Optional
from pydantic import BaseModel, Field, validator
from beanie import Document, Link, PydanticObjectId
from fastapi import UploadFile

from app.models.base import TimestampMixin
from app.models.user import User, UserPublic

class PaperBase(TimestampMixin):
    file_name: str = Field(..., min_length=1, max_length=255)
    url: Optional[str] = Field(None, max_length=512)
    is_process: bool = Field(default=True, index=True)

class PaperCreate(PaperBase):
    file_name: str = Field(..., min_length=1, max_length=255)
    is_process: bool = Field(default=True, index=True)

class PaperCreateForm(BaseModel):
    """用于处理文件上传表单的Pydantic模型"""
    file_name: str
    file: UploadFile
    is_process: bool = True
    
    # 告诉Pydantic这个字段不是JSON可序列化的
    class Config:
        arbitrary_types_allowed = True
    
    @validator('file')
    def validate_file(cls, v):
        """验证上传的文件"""
        # 可以添加文件类型、大小等验证
        if not v.filename:
            raise ValueError("文件名不能为空")
        return v
    
    def to_paper_create(self) -> PaperCreate:
        """转换为PaperCreate模型"""
        return PaperCreate(
            file_name=self.file_name,
            is_process=self.is_process
        )

class PaperUpdate(BaseModel):
    file_name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = Field(None, max_length=512)
    is_process: Optional[bool] = None

class Paper(PaperBase, Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    owner: Link["User"] = Field(
        default=None,
    )

    class Settings:
        name = "papers"
        use_state_management = True

    async def to_public(self) -> "PaperPublic":
        """转换为公共项目模型"""
        owner = await self.owner.fetch() if isinstance(self.owner, Link) else self.owner
        if not owner:
            raise ValueError("Owner not found")

        return PaperPublic(
            id=self.id,
            file_name=self.file_name,
            url=self.url,
            is_process=self.is_process,
            created_at=self.created_at,
            updated_at=self.updated_at,
            owner=owner.to_public(),
        )

class PaperPublic(PaperBase):
    id: PydanticObjectId = Field(alias="id")
    owner: UserPublic

    @classmethod
    async def from_item(cls, paper: Paper) -> "PaperPublic":
        """从项目创建公共项目模型"""
        return await paper.to_public()

class PapersPublic(BaseModel):
    data: list[PaperPublic]
    count: int 