import uuid

from fastapi import APIRouter
from sqlmodel import select
from fastapi_pagination import Page
from fastapi.exceptions import HTTPException
from fastapi_pagination.ext.sqlmodel import paginate

from app.api.deps import SessionDep, CurrentUser
from app.models import Task, TaskGroup
from app.schemas import TaskGroupCreate, TaskGroupPubilc, TaskCreate, TaskOut
from app.services.task import TaskService
from app.tasks.task import execute_script_content

router = APIRouter(prefix="/group", tags=["Tasks"])


@router.get("/", response_model=Page[TaskGroup])
def get_groups(session: SessionDep):
    """获取任务组列表"""
    statement = select(TaskGroup)
    return paginate(session, statement)


@router.post("/", response_model=TaskGroupPubilc)
def create_group(session: SessionDep, current_user: CurrentUser, group_obj: TaskGroupCreate):
    """任务组创建"""
    group = TaskGroup(**group_obj.model_dump(), create_by=current_user.id)
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


@router.get("/{group_id}", response_model=TaskGroupPubilc)
def get_group(session: SessionDep, group_id: int):
    """获取任务组详情"""
    group = session.get(TaskGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.get("/{group_id}/task", response_model=Page[TaskOut])
def get_tasks(session: SessionDep, group_id: int):
    statement = select(Task).where(Task.group_id == group_id)
    return paginate(session, statement)


@router.post("/{group_id}/task", response_model=TaskOut)
def create_task(session: SessionDep, group_id: int, task_obj: TaskCreate, current_user: CurrentUser):
    """创建任务"""
    task = TaskService.create_task(
        db=session, task_create=task_obj, group_id=group_id, user_id=current_user.id
    )

    return task


@router.post("/{group_id}/task/{task_id}")
def run_task(session: SessionDep, group_id: int, task_id: uuid.UUID):
    """运行任务"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    result = execute_script_content.delay(task.task_script, "python", {"timeout": 10})
    print(result)
    return {"hello"}
