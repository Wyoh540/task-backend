from sqlmodel import Session, select

from app.models import Tag


class TagManage:
    """Tag 管理"""

    @classmethod
    def get_or_create_tag(cls, db: Session, tag_name: str) -> Tag:
        """Get or create a tag by name."""
        existing_tag = db.exec(select(Tag).where(Tag.name == tag_name)).first()
        if not existing_tag:
            new_tag = Tag(name=tag_name)
            db.add(new_tag)
            db.commit()
            db.refresh(new_tag)

            existing_tag = new_tag
        return existing_tag
