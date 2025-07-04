import uuid
from typing import Any, Literal
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, TEXT
from pydantic import computed_field
from celery.result import AsyncResult

from app.models.job import Language, Team, WorkNode
from app.schemas.user import UserPubic


class TeamBase(SQLModel):
    """任务组基类"""

    name: str
    description: str


class TeamCreate(TeamBase):
    """任务空间创建"""

    pass


class TeamUpdate(SQLModel):
    """任务组更新"""

    name: str | None
    description: str | None


class TeamPubilc(TeamBase):
    """任务组公共信息"""

    id: int | None = Field(primary_key=True, default=None)
    name: str = Field(max_length=20)
    description: str = Field(sa_type=TEXT(), nullable=True)
    create_by: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")

    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobBase(SQLModel):
    name: str
    description: str | None = None
    script_content: str | None = None
    script_path: str | None = None


class JobOut(JobBase):
    id: int
    language: Language
    team: Team
    owner: UserPubic


class JobCreate(JobBase):
    language_id: int


class JobUpdate(JobBase):
    pass


class WorkNodeCreate(SQLModel):
    """工作节点创建"""

    node_ip: str
    node_name: str
    status: WorkNode.NodeStatus = WorkNode.NodeStatus.ONLINE


class TaskResult(SQLModel):
    """任务执行结果详情"""

    task_id: uuid.UUID

    @computed_field
    @property
    def status(self) -> Literal["PENDING", "STARTED", "SUCCESS", "FAILURE", "RETRY"]:
        """任务状态"""
        result = AsyncResult(str(self.task_id))
        return result.status

    @computed_field
    @property
    def result(self) -> Any | None:
        """任务执行结果"""
        result = AsyncResult(str(self.task_id))
        return result.result if result.successful() else None

    @computed_field
    @property
    def date_done(self) -> datetime | None:
        """任务完成时间"""
        result = AsyncResult(str(self.task_id))
        return result.date_done if result.successful() else None


class TaskResultList(SQLModel):
    """任务执行结果列表"""

    task_id: uuid.UUID

    @computed_field
    @property
    def status(self) -> Literal["PENDING", "STARTED", "SUCCESS", "FAILURE", "RETRY"]:
        """任务状态"""
        result = AsyncResult(str(self.task_id))
        return result.status

    @computed_field
    @property
    def date_done(self) -> datetime | None:
        """任务完成时间"""
        result = AsyncResult(str(self.task_id))
        return result.date_done if result.successful() else None
