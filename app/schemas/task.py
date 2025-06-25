import uuid
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, TEXT

from app.models.task import Language, TaskGroup, WorkNode
from app.schemas.user import UserPubic


class TaskGroupBase(SQLModel):
    """任务组基类"""

    name: str
    description: str


class TaskGroupCreate(TaskGroupBase):
    """任务组创建"""

    pass


class TaskGroupUpdate(TaskGroupBase):
    """任务组更新"""

    name: str | None
    description: str | None


class TaskGroupPubilc(TaskGroupBase):
    """任务组公共信息"""

    id: int | None = Field(primary_key=True, default=None)
    name: str = Field(max_length=20)
    description: str = Field(sa_type=TEXT(), nullable=True)
    create_by: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")

    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TaskBase(SQLModel):
    task_name: str
    description: str | None = None
    task_script: str | None = None
    script_path: str | None = None


class TaskOut(TaskBase):
    id: uuid.UUID
    language: Language
    group: TaskGroup
    owner: UserPubic


class TaskCreate(TaskBase):
    language_id: int


class TaskUpdate(TaskBase):
    pass



class WorkNodeCreate(SQLModel):
    """工作节点创建"""

    node_ip: str
    node_name: str
    status: WorkNode.NodeStatus = WorkNode.NodeStatus.ONLINE