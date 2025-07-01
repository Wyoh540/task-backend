from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep
from app.services import login
from app import schemas
from app.core.config import settings
from app.core import security

router = APIRouter(prefix="/login", tags=["Login"])


@router.post("/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> schemas.Token:
    # Your logic to validate the user and generate a token goes here.

    user = login.authenticate(session=session, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    elif not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return schemas.Token(
        access_token=security.create_access_token(user.id, expires_delta=access_token_expire),
    )
