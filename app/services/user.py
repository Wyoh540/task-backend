from sqlmodel import Session, select


from app.models import User
from app.schemas.user import UserPubic, UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:
    """用户管理"""

    @classmethod
    def create_user(cls, db: Session, user_create: UserCreate) -> UserPubic:
        """创建用户"""
        user = db.exec(select(User).where(User.username == user_create.username)).first()
        if not user:
            user = User.model_validate(user_create, update={"hashed_password": get_password_hash(user_create.password)})
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    @classmethod
    def update_user(cls, db: Session, user: User, user_update: UserUpdate) -> UserPubic:
        """更新用户信息"""
        user.sqlmodel_update(user, update=user_update.model_dump(exclude_unset=True))
        db.add(user)
        db.commit()
        db.refresh(user)
        return user