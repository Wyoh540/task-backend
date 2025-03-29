from pydantic import EmailStr
from sqlmodel import SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr | None = None
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: str | None = None


class UserInDBBase(UserBase):
    id: int | int = None


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


class UserPubic(SQLModel):
    id: int | None = None
    email: EmailStr | None = None
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


class UsersPublic(SQLModel):
    data: list[UserPubic]
