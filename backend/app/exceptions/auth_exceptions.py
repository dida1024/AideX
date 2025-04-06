from app.exceptions.base import BizException


class AuthFail(BizException):
    """验证失败"""
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(code=10201, message=message)

class PermissionDenied(BizException):
    """权限不足"""
    def __init__(self, message: str = "The user doesn't have enough privileges"):
        super().__init__(code=10202, message=message)

class UserEmailOrPasswordFail(BizException):
    """用户名或密码错误"""
    def __init__(self, message: str = "业务异常"):
        super().__init__(code=10203, message=message)

class SuperCanNotDeleteSelf(BizException):
    """超级用户禁止删除自身"""
    def __init__(self,message: str = "Super users are not allowed to delete themselves"):
        super().__init__(code=10204, message=message)