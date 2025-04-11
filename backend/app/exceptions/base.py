
# 基础异常
class BizException(Exception):
    """基础业务异常"""
    def __init__(self, code: int = 400, message: str = "业务异常"):
        self.code = code
        self.message = message
    
class ParamException(BizException):
    """参数错误"""
    def __init__(self, message: str = "param error"):
        super().__init__(code=10001,message=message)