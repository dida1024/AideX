
# 基础异常
class BizException(Exception):
    """基础业务异常"""
    def __init__(self, code: int = 400, message: str = "业务异常"):
        self.code = code
        self.message = message