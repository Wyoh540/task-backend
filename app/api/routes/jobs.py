import uuid

from fastapi import APIRouter
from sqlmodel import select
from fastapi_pagination import Page
from fastapi.exceptions import HTTPException
from fastapi_pagination.ext.sqlmodel import paginate
from celery.result import AsyncResult

from app.api.deps import SessionDep, CurrentUser
from app.models import Job, Team
from app.schemas import (
    TeamCreate,
    TeamPubilc,
    JobCreate,
    JobOut,
    TaskResult,
)
from app.services.job import JobService
from app.tasks.task import execute_script_content
from app.celery import celery_app

router = APIRouter(prefix="/group", tags=["Tasks"])


@router.get("/", response_model=Page[Team])
def get_teams(session: SessionDep):
    """获取空间列表"""
    statement = select(Team)
    return paginate(session, statement)


@router.post("/", response_model=TeamPubilc)
def create_team(session: SessionDep, current_user: CurrentUser, team_obj: TeamCreate):
    """空间创建"""
    team = Team(**team_obj.model_dump(), create_by=current_user.id)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@router.get("/{team_id}", response_model=TeamPubilc)
def get_team(session: SessionDep, team_id: int):
    """获取空间详情"""
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.get("/{team_id}/job", response_model=Page[JobOut])
def get_tasks(session: SessionDep, team_id: int):
    statement = select(Job).where(Job.team_id == team_id)
    return paginate(session, statement)


@router.post("/{team_id}/job", response_model=JobOut)
def create_task(session: SessionDep, team_id: int, task_obj: JobCreate, current_user: CurrentUser):
    """创建任务"""
    job = JobService.create_task(db=session, task_create=task_obj, team_id=team_id, user_id=current_user.id)

    return job


@router.post("/{team_id}/job/{job_id}", response_model=TaskResult)
def run_task(session: SessionDep, team_id: int, job_id: int):
    """运行任务"""
    task = session.get(Job, job_id)
    if not task:
        raise HTTPException(status_code=404, detail="Job not found")
    result = execute_script_content.apply_async(
        (task.task_script, "python", {"timeout": 10}), ignore_result=task.ignore_result
    )
    return {
        "run_id": result.id,
        "status": result.status,
        "result": result.result if result.successful() else None,
        "date_done": result.date_done,
    }


@router.get("/{team_id}/job/{job_id}/result/{task_id}", response_model=TaskResult)
def get_task_result(task_id: str):
    """获取celery任务执行结果"""
    async_result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": async_result.status,
        "result": async_result.result if async_result.successful() else None,
        "date_done": async_result.date_done,
    }
