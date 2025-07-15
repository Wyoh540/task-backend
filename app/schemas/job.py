import uuid
from typing import Any, Literal
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, TEXT
from pydantic import computed_field, model_serializer, ConfigDict
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

    jobs: list["JobOut"]

    @computed_field
    @property
    def job_count(self) -> int:
        return len(self.jobs)

    @model_serializer
    def ser_model(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "create_by": self.create_by,
            "create_at": self.create_at,
            "update_at": self.update_at,
            "job_count": self.job_count,
        }

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "admin",
                    "description": "admin 空间",
                    "create_by": 1,
                    "create_at": "2025-07-05T09:56:14",
                    "update_at": "2025-07-05T09:56:14",
                    "job_count": 1,
                }
            ]
        }
    )


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
