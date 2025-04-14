import os
from typing import Union
from fastapi import File, UploadFile
import aiofiles  # 用于异步文件操作
import logging
from app.core.config import settings

from app.exceptions.file_exceptions import FileTypeError  # 用于日志记录

logger = logging.getLogger(__name__)


class FileHelper:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)

    def _prepare_file_path(self, full_path: str) -> bool:
        """创建文件夹并删除已存在的文件"""
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            if os.path.isfile(full_path):
                os.remove(full_path)
            return True
        except Exception as e:
            self.logger.error(f"Error preparing file path: {e}")
            return False

    async def _write_file(self, full_path: str, content: Union[str, bytes], binary: bool = False) -> bool:
        """异步写入文件内容"""
        if not self._prepare_file_path(full_path):
            return False

        try:
            mode = "wb" if binary else "w"
            async with aiofiles.open(full_path, mode) as file:
                await file.write(content)
            return True
        except Exception as e:
            self.logger.error(f"Error writing file: {e}")
            return False
    
    def _check_file_exit(self, file_name: str) -> bool:
        """检查文件是否存在
        
        Args:
            file_name: 文件名
            
        Returns:
            bool: 文件是否存在
        """
        full_path = os.path.join(self.file_path, file_name)
        return os.path.exists(full_path)

    def save_file(self, file_name: str, content: Union[str, bytes]) -> bool:
        """保存字符串或字节流到文件"""
        full_path = os.path.join(self.file_path, file_name)
        if not self._prepare_file_path(full_path):
            return False
        is_binary = isinstance(content, bytes)
        return self._write_file(full_path, content, binary=is_binary)

    async def save_from_upload_file(self, file: UploadFile, file_name: str = None) -> str:
        """从 FastAPI 的 UploadFile 对象保存文件"""
        if not file_name:
            file_name = file.filename

        full_path = os.path.join(self.file_path, file_name)

        if not self._prepare_file_path(full_path):
            return False

        content = await file.read()
        is_binary = isinstance(content, bytes)
        await self._write_file(full_path, content, binary=is_binary)
        return file_name
    
    @staticmethod
    async def validate_upload_file(file: UploadFile = File(...), allowed_types: list[str] = None) -> UploadFile:
        """
        验证上传文件的依赖项
        
        参数:
            file: 上传的文件
            allowed_types: 允许的文件MIME类型列表，默认仅允许markdown文件
        
        返回:
            验证通过的文件对象
            
        异常:
            FileTypeError: 当文件类型不在允许列表中时抛出
        """
        # 默认仅允许markdown文件
        if allowed_types is None:
            allowed_types = ["application/md"]
        
        logger.info("file_type: %s", file.content_type)
            
        if file.content_type not in allowed_types:
            raise FileTypeError
        return file
        
    
    def gen_full_path(self, file_name: str) -> str:
        """生成文件的完整路径"""
        is_exit = self._check_file_exit(file_name=file_name)
        if not is_exit:
            return ""
        return os.path.join(self.file_path, file_name)
    
    def gen_down_url(self, saved_file_name:str) -> str:
        """生成文件的下载地址"""
        return f"{settings.BACKEND_HOST}/api/v1/utils/download/?file_name={saved_file_name}"