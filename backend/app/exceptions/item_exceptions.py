from app.exceptions.base import BizException


class ItemNotFound(BizException):
    """用户未找到异常"""
    def __init__(self, message: str = "Item not found"):
        super().__init__(code=10301, message=message)
