import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.exceptions.file_exceptions import FileNotFound
from app.models.response import ApiResponse
from app.utils.email_helper import generate_test_email, send_email
from app.core.config import settings
from app.utils.file_helper import FileHelper

router = APIRouter(prefix="/utils", tags=["utils"])

logger = logging.getLogger(__name__)


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
    response_model=ApiResponse[None],
)
def test_email(email_to: EmailStr) -> ApiResponse:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return ApiResponse.success_response(
        message="测试邮件已发送",
        code=201
    )


@router.get("/health-check/", response_model=ApiResponse[bool])
async def health_check() -> ApiResponse:
    return ApiResponse.success_response(
        data=True,
        message="服务正常"
    )

@router.get("/download/")
async def download(
        file_name: Optional[str] = Query(None, max_length=255)
):
    file_helper = FileHelper(settings.DOWNLOAD_DIR)
    file_url = file_helper.gen_full_path(file_name)
    if file_url == "":
        raise FileNotFound
    return FileResponse(
        path=file_url,
        filename=file_name,
        media_type="application/octet-stream",
    )
