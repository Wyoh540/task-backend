import uuid
from typing import Any, Literal
from datetime import datetime, timezone

from sqlmodel import SQLModel, TEXT
from pydantic import computed_field, field_serializer, Field
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


class TeamPubilc(SQLModel):
    """任务组公共信息"""

    id: int
    name: str
    description: str
    create_by: int

    create_at: datetime
    update_at: datetime

    jobs: list["JobOut"] = Field(serialization_alias="job_count")

    @field_serializer("jobs")
    def job_count(self, jobs: list["JobOut"]) -> int:
        return len(self.jobs)


class JobBase(SQLModel):
    name: str
    description: str | None = None
    script_content: str | None = None
    script_path: str | None = None


class JobOut(JobBase):
    id: int
    language: Language
    team_id: int
    # team: Team
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


class TeamMemberBase(SQLModel):
    user_id: int
    is_admin: bool = False


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMemberUpdate(SQLModel):
    is_admin: bool | None = None


class TeamMemberPublic(TeamMemberBase):
    id: int
    user: UserPubic | None = None


class TeamMemberList(SQLModel):
    id: int
    user: UserPubic | None = None
    is_admin: bool


class CreateLanguage(SQLModel):

    language_name: str