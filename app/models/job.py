import uuid
from enum import Enum
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import TEXT

from app.models.user import User


class Language(SQLModel, table=True):
    """语言表"""

    __tablename__ = "language"

    id: int | None = Field(primary_key=True, default=None)
    language: str = Field(max_length=20, unique=True)


class Team(SQLModel, table=True):
    """任务空间表"""

    __tablename__ = "team"

    id: int | None = Field(primary_key=True, default=None)
    name: str = Field(max_length=20)
    description: str = Field(sa_type=TEXT(), nullable=True)
    create_by: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")

    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Job(SQLModel, table=True):
    """任务信息表"""

    __tablename__ = "job"

    id: int = Field(primary_key=True, default=None, description="任务ID")
    name: str = Field(max_length=20, nullable=False, description="任务名称")
    description: str | None = Field(max_length=100, nullable=True, description="任务描述")
    script_content: str | None = Field(sa_type=TEXT(), nullable=True, description="任务脚本内容")
    script_path: str | None = Field(nullable=True, description="脚本文件路径")
    ignore_result: bool = Field(default=False, nullable=False, description="是否忽略结果")

    language_id: int = Field(foreign_key="language.id")
    team_id: int = Field(foreign_key="team.id", nullable=False, ondelete="CASCADE")
    owner_id: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")

    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    language: Language = Relationship()
    team: Team = Relationship()
    owner: User = Relationship()


class JobTasks(SQLModel, table=True):
    """任务执行结果关联表"""

    __tablename__ = "job_tasks"

    id: int | None = Field(primary_key=True, default=None, description="主键ID")
    job_id: int = Field(foreign_key="job.id", nullable=False, ondelete="CASCADE", description="任务ID")
    task_id: uuid.UUID = Field(max_length=36, nullable=False, description="运行ID")


class WorkNode(SQLModel, table=True):
    """工作节点表"""

    __tablename__ = "work_node"

    class NodeStatus(int, Enum):
        """节点状态"""

        ONLINE = 1
        OFFLINE = 2

    id: int | None = Field(primary_key=True, default=None, description="工作节点ID")
    node_ip: str = Field(max_length=15, nullable=False, unique=True, description="节点IP地址")
    node_name: str = Field(max_length=60, nullable=False)
    status: NodeStatus = Field(default=NodeStatus.OFFLINE, nullable=False, description="节点状态, 1:在线, 2: 离线")
    last_ping: datetime | None = Field(default=None, nullable=True, description="最后心跳时间")
    platform: str | None = Field(default=None, nullable=True, description="操作系统平台")

    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TeamMember(SQLModel, table=True):
    """空间成员表，含管理员标记"""

    __tablename__ = "team_member"

    id: int | None = Field(primary_key=True, default=None)
    team_id: int = Field(foreign_key="team.id", nullable=False, ondelete="CASCADE")
    user_id: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    is_admin: bool = Field(default=False, nullable=False, description="是否为管理员")

    # 可选：创建时间等字段
    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User = Relationship()
