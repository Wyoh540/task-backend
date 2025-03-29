from sqlmodel import create_engine, Session

from app.core.config import settings
from app.schemas.user import UserCreate
from app.services.user import UserService

# connect_args = {"check_same_thread": False}  # 仅SQLite 配置，不同线程中使用同一个数据库
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user_in = UserCreate(
        email=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        is_superuser=True,
    )
    UserService.create_user(db=session, user_create=user_in)
    # user = crud.create_user(session=session, user_create=user_in)
