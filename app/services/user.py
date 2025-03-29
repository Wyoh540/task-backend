from sqlmodel import Session, select


from app.models import User
from app.schemas.user import UserPubic, UserCreate
from app.core.security import get_password_hash


class UserService:
    """用户管理"""

    @classmethod
    def create_user(cls, db: Session, user_create: UserCreate) -> UserPubic:
        """创建用户"""
        user = db.exec(select(User).where(User.email == user_create.email)).first()
        if not user:
            user = User.model_validate(
                user_create, update={"hashed_password": get_password_hash(user_create.password)}
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
