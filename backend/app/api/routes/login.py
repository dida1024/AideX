from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
import logging

from app import crud
from app.api.deps import CurrentUser, CurrentSuperuser
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import MessageResponse, PasswordResetConfirm, Token, UserPublic
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    user = await crud.authenticate(
        email=form_data.username, password=form_data.password
    )
    if not user:
        logger.warning(f"Authentication failed for user: {form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        logger.warning(f"Inactive user attempt: {form_data.username}")
        raise HTTPException(status_code=400, detail="Inactive user")
    
    logger.info(f"Creating access token for user: {user.id}")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    logger.info(f"Access token created successfully for user: {user.id}")
    return Token(access_token=token)


@router.post("/login/test-token", response_model=UserPublic)
async def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
async def recover_password(email: str) -> MessageResponse:
    """
    Password Recovery
    """
    user = await crud.get_user_by_email(email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return MessageResponse(MessageResponse="Password recovery email sent")


@router.post("/reset-password/")
async def reset_password(body: PasswordResetConfirm) -> MessageResponse:
    """
    Reset password
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await crud.get_user_by_email(email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    user.hashed_password = get_password_hash(password=body.new_password)
    await user.save()
    return MessageResponse(MessageResponse="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(CurrentSuperuser)],
    response_class=HTMLResponse,
)
async def recover_password_html_content(email: str) -> Any:
    """
    HTML Content for Password Recovery
    """
    user = await crud.get_user_by_email(email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
