from typing import Annotated

import jwt
import logging
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from beanie.odm.fields import PydanticObjectId

from app.core import security
from app.core.config import settings
from app.models import TokenData, User
from app.exceptions.user_exceptions import UserNotFound, UserNotActive
from app.exceptions.auth_exceptions import AuthFail, PermissionDenied

logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]

async def get_current_user(token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenData(**payload)
        user_id = PydanticObjectId(token_data.sub)
        user = await User.get(user_id)
        
        if not user:
            raise UserNotFound
        if not user.is_active:
            raise UserNotActive
        return user
    except (InvalidTokenError, ValidationError) as e:
        logger.error(f"Token validation error: {str(e)}")
        raise AuthFail

CurrentUser = Annotated[User, Depends(get_current_user)]

async def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise PermissionDenied
    return current_user

CurrentSuperuser = Annotated[User, Depends(get_current_active_superuser)] 