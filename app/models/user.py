from enum import Enum

from sqlmodel import SQLModel, Field
from sqlalchemy import Integer, Column
from pydantic import EmailStr


class User(SQLModel, table=True):
    """用户表"""

    class LevelEnum(int, Enum):
        USER = 1
        VIP = 2

    id: int | None = Field(primary_key=True, default=None)
    username: str = Field(max_length=24, unique=True, default=None)
    email: EmailStr | None = Field(max_length=50, unique=True, default=None)
    phone: str | None = Field(max_length=20, unique=True, default=None)
    level: LevelEnum = Field(sa_column=Column(Integer), default=LevelEnum.USER.value)
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
