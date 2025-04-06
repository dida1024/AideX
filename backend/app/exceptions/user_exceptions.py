from app.exceptions.base import BizException


class UserNotFound(BizException):
    """用户未找到异常"""
    def __init__(self, message: str = "User not found"):
        super().__init__(code=10101, message=message)

class UserNotActive(BizException):
    """User not active"""
    def __init__(self, code: int = 10102, message: str = "Inactive user"):
        super().__init__(code, message)

class UserCreateFail(BizException):
    """User create fail"""
    def __init__(self, code: int = 10103, message: str = "An error occurred while creating the user."):
        super().__init__(code, message)

class UserExists(BizException):
    """User Exists"""
    def __init__(self, code: int = 10104, message: str = "User with this email already exists"):
        super().__init__(code, message)

class PasswordSame(BizException):
    """New password cannot be the same as the current one"""
    def __init__(self, code: int = 10105, message: str = "New password cannot be the same as the current one"):
        super().__init__(code, message)

class IncorrectPassword(BizException):
    """IncorrectPassword"""
    def __init__(self, code: int = 10106, message: str = "IncorrectPassword"):
        super().__init__(code, message)