import psutil

from fastapi import APIRouter
from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination import Page
from sqlmodel import select

from app.api.deps import SessionDep
from app.models.task import WorkNode

router = APIRouter(prefix="/worker", tags=["Worker"])


@router.get("/", response_model=Page[WorkNode])
def list_worker(session: SessionDep):
    """获取所有 worker 的状态"""
    statement = select(WorkNode)
    return paginate(session, statement)