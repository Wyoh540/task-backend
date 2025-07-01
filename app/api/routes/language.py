from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import SessionDep
from app.models.job import Language

router = APIRouter(prefix="/language", tags=["Language"])


@router.get("/", response_model=list[Language])
def get_languages(session: SessionDep):
    """获取所有语言"""
    statement = select(Language)
    languages = session.exec(statement).all()

    return languages
