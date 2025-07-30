import jwt

from datetime import timedelta, datetime

from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas.apikeys import ApiKeysBase
from app.services.user_service import UserService

from app.utils.constant import ROLES, PERMISSIONS
from app.utils.env import get_token_expire_minutes
from app.utils.jw_utils import Token, create_access_token, authenticate_user, get_user

from typing import Annotated

from fastapi import HTTPException, Depends
from starlette import status

from jwt.exceptions import InvalidTokenError

from app.dependencies import ALGORITHM, oauth2_scheme, get_cache, get_tracer
from app.schemas.apikeys import ApiKeysVerify
from app.schemas.user import User
from app.services.auth_service import AuthenticateService
from app.utils.env import get_key
from app.utils.jw_utils import TokenData

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm,
        Depends()], session: AsyncSession = Depends(get_session), cache=Depends(get_cache),
                    tracer=Depends(get_tracer)) -> Token:
    with tracer.start_as_current_span("login-for-access-token") as parent_span:

        # Child Span: Authenticate user
        with tracer.start_as_current_span("authenticate-user") as span_auth:
            user = await authenticate_user(form_data.username, form_data.password, session, cache, tracer)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Child Span: Permission check
        with tracer.start_as_current_span("check-user-permission") as span_check_permission:
            await is_allowed_to_generate_token(user, session, cache, tracer)

        # Child Span: Create access token
        with tracer.start_as_current_span("create-access-token") as create_token:
            access_token_expires = timedelta(minutes=int(get_token_expire_minutes()))
            access_token = create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )

        # Child Span: Save token in DB
        with tracer.start_as_current_span("save-api-key") as save_token_db:
            now = datetime.now()
            db_api_key = ApiKeysBase(
                api_key=access_token,
                user_id=user.id,
                expires_at=now + access_token_expires,
                is_active=True
            )
            await AuthenticateService.service_create_api_key(db_api_key, session, cache, tracer)

        return Token(access_token=access_token, token_type="bearer")


async def is_allowed_to_generate_token(user, session: AsyncSession, cache, tracer):
    role = await UserService.get_user_role(user.id, session, cache, tracer)

    if not role or role is None:
        raise HTTPException(status_code=404,
                            detail="The username is not allowed to generate a token.")
    permission = next(
        (p for p in await UserService.get_role_permission(ROLES.API_USER.value, session, cache, tracer)
         if p.permission_name == PERMISSIONS.API_GENERATE_TOKEN.value),
        None
    )
    if not permission or permission is None:
        raise HTTPException(status_code=404,
                            detail="The username is not allowed to generate a token.")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, get_key(), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

        user = UserService.get_user_by_username(token_data.username)

        key = ApiKeysVerify(
            api_key=token,
            user_id=user.id
        )
        is_valid = AuthenticateService.is_api_key_active(key)

        await AuthenticateService.is_api_key_expired_set_inactive(token)

        if not is_valid:
            raise HTTPException(status_code=401,
                                detail="The API key validation was unsuccessful.")
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(username=token_data.username)

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)],):
    if current_user.is_disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
