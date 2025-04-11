from app.exceptions.base import BizException


class FileNotFound(BizException):
    """文件未找到异常"""
    def __init__(self, message: str = "File not found"):
        super().__init__(code=10401, message=message)

class FileTypeError(BizException):
    """文件类型错误"""
    def __init__(self, message: str = "File type error"):
        super().__init__(code=10402,message=message)