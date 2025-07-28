from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import SessionDep
from app.models.job import Language
from app.schemas import CreateLanguage

router = APIRouter(prefix="/language", tags=["Language"])


@router.get("/", response_model=list[Language])
def list_languages(session: SessionDep):
    """获取所有语言"""
    statement = select(Language)
    languages = session.exec(statement).all()

    return languages

@router.post("/", response_model=Language)
def create_language(session: SessionDep, language_in: CreateLanguage):
    """创建一个语言"""
    language = Language(language=language_in.language_name)
    session.add(language)
    session.commit()
    session.refresh(language)
    
    return language
