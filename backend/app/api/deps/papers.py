import logging
from typing import Callable
from functools import partial
from fastapi import File, Form, UploadFile, Depends

from app.exceptions.base import ParamException
from app.exceptions.file_exceptions import FileTypeError
from app.models.papers import PaperCreateForm
from app.utils.file_helper import FileHelper

logger = logging.getLogger(__name__)

# 定义论文允许的文件类型
PAPER_ALLOWED_TYPES = [
    # Markdown文件
    "text/markdown",                     # 标准Markdown MIME类型
    "text/plain",                        # 纯文本(可能包含md文件)
    "text/x-markdown",                   # 备用Markdown MIME类型
    
    # PDF文件
    "application/pdf",                   # PDF标准类型
    
    # Word文档
    "application/msword",                # .doc格式
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document" # .docx格式
]

# 创建一个特定于论文的文件验证依赖
# 不使用partial，而是创建一个真正的异步函数
async def validate_paper_file(file: UploadFile = File(...)) -> UploadFile:
    """验证论文文件类型"""
    return await FileHelper.validate_upload_file(file, allowed_types=PAPER_ALLOWED_TYPES)

async def get_paper_form(
    file_name: str = Form(..., min_length=1, max_length=255),
    file: UploadFile = Depends(validate_paper_file),
    is_process: bool = Form(default=True)
) -> PaperCreateForm:
    """获取并验证表单数据"""
    try:
        return PaperCreateForm(
            file_name=file_name,
            file=file,
            is_process=is_process
        )
    except ValueError as e:
        logger.error(e)
        raise ParamException 