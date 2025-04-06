from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.base import BizException


# @app.exception_handler(BizException)
async def biz_exception_handler(request: Request, exc: BizException):
    return JSONResponse(
        status_code=200,  # 不抛 HTTP 错
        content={
            "code": exc.code,
            "msg": exc.message,
            "data": None
        },
    )