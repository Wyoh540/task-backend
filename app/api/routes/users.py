from typing import Any

from fastapi import APIRouter
from sqlmodel import select

from app.models import User
from app.core.security import get_password_hash
from app.api.deps import SessionDep, CurrentUser
from app.schemas import UsersPublic, UserCreate, UserPubic
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UsersPublic)
def get_users(session: SessionDep) -> Any:
    """获取所有用户列表"""
    statement = select(User)
    users = session.exec(statement).all()
    return UsersPublic(data=users)


@router.post("/", response_model=UserPubic)
def create_user(session: SessionDep, user_in: UserCreate) -> Any:
    """创建用户"""
    user = UserService.create_user(db=session, user_create=user_in)
    return user


@router.get("/me", response_model=UserPubic)
def get_user_me(current_user: CurrentUser) -> Any:
    return current_user
