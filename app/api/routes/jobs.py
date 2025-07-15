import uuid

from fastapi import APIRouter, status
from sqlmodel import select
from fastapi_pagination import Page
from fastapi.exceptions import HTTPException
from fastapi_pagination.ext.sqlmodel import paginate
from celery.result import AsyncResult

from app.api.deps import SessionDep, CurrentUser
from app.models import Job, Team, JobTasks, TeamMember, User
from app.schemas import (
    TeamCreate,
    TeamPubilc,
    JobCreate,
    JobOut,
    TaskResultList,
    TaskResult,
    TeamMemberCreate,
    TeamMemberUpdate,
    TeamMemberPublic,
    TeamMemberList,
)
from app.services.job import JobService
from app.tasks.task import execute_script_content
from app.celery import celery_app
from app.schemas.user import UserPubic

router = APIRouter(prefix="/team", tags=["Tasks"])


@router.get("/", response_model=Page[TeamPubilc])
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
def create_task(session: SessionDep, team_id: int, job_obj: JobCreate, current_user: CurrentUser):
    """创建任务"""
    job = JobService.create_job(db=session, job_create=job_obj, team_id=team_id, user_id=current_user.id)

    return job


@router.post("/{team_id}/job/{job_id}", response_model=TaskResult)
def run_task(session: SessionDep, team_id: int, job_id: int):
    """运行任务"""
    task = session.get(Job, job_id)
    if not task:
        raise HTTPException(status_code=404, detail="Job not found")
    result = execute_script_content.apply_async(
        (task.script_content, "python", {"timeout": 10}), ignore_result=task.ignore_result
    )
    job_task = JobTasks(
        job_id=job_id,
        task_id=uuid.UUID(result.id),
    )
    session.add(job_task)
    session.commit()
    session.refresh(job_task)
    return job_task


@router.get("/{team_id}/job/{job_id}/result/", response_model=Page[TaskResultList])
def list_job_tasks(session: SessionDep, team_id: int, job_id: int):
    """获取任务执行结果列表"""
    statement = select(JobTasks).where(JobTasks.job_id == job_id)
    return paginate(session, statement)


@router.get("/{team_id}/job/{job_id}/result/{task_id}", response_model=TaskResult)
def get_task_result(session: SessionDep, team_id: int, job_id: int, task_id: str):
    """获取celery任务执行结果"""
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    async_result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": async_result.status,
        "result": async_result.result if async_result.successful() else None,
        "date_done": async_result.date_done,
    }


@router.delete("/{team_id}/job/{job_id}/result/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_result(session: SessionDep, team_id: int, job_id: int, task_id: str):
    """删除任务结果"""
    statement = select(JobTasks).where(JobTasks.task_id == uuid.UUID(task_id))
    task_result = session.exec(statement).first()

    session.delete(task_result)
    session.commit()


@router.post("/{team_id}/members", response_model=TeamMemberPublic)
def add_team_member(session: SessionDep, team_id: int, member: TeamMemberCreate):
    """添加空间成员（可指定是否为管理员）"""
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    user = session.get(User, member.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # 检查是否已存在
    statement = select(TeamMember).where((TeamMember.team_id == team_id) & (TeamMember.user_id == member.user_id))
    if session.exec(statement).first():
        raise HTTPException(status_code=400, detail="User already in team")
    team_member = TeamMember(team_id=team_id, user_id=member.user_id, is_admin=member.is_admin)
    session.add(team_member)
    session.commit()
    session.refresh(team_member)
    return team_member


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_team_member(session: SessionDep, team_id: int, user_id: int):
    """移除空间成员"""
    statement = select(TeamMember).where((TeamMember.team_id == team_id) & (TeamMember.user_id == user_id))
    member = session.exec(statement).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    session.delete(member)
    session.commit()


@router.patch("/{team_id}/members/{user_id}", response_model=TeamMemberPublic)
def update_team_member(session: SessionDep, team_id: int, user_id: int, update: TeamMemberUpdate):
    """设置/取消管理员"""
    statement = select(TeamMember).where((TeamMember.team_id == team_id) & (TeamMember.user_id == user_id))
    member = session.exec(statement).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if update.is_admin is not None:
        member.is_admin = update.is_admin
    session.add(member)
    session.commit()
    session.refresh(member)
    return member


@router.get("/{team_id}/members", response_model=Page[TeamMemberList])
def list_team_members(session: SessionDep, team_id: int):
    """获取空间成员列表（含管理员标记）"""
    statement = select(TeamMember).where(TeamMember.team_id == team_id)

    return paginate(session=session, query=statement)
