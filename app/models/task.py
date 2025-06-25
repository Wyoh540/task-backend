import uuid
from enum import Enum
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import TEXT

from app.models.user import User


class Language(SQLModel, table=True):
    """语言表"""

    id: int | None = Field(primary_key=True, default=None)
    language: str = Field(max_length=20, unique=True)


class TaskGroup(SQLModel, table=True):
    """任务分组表"""

    id: int | None = Field(primary_key=True, default=None)
    name: str = Field(max_length=20)
    description: str = Field(sa_type=TEXT(), nullable=True)
    create_by: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")

    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Task(SQLModel, table=True):
    """任务信息表"""

    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    task_name: str = Field(max_length=20, nullable=False)
    description: str | None = Field(max_length=100, nullable=True)
    task_script: str | None = Field(sa_type=TEXT(), nullable=True)
    script_path: str | None = Field(nullable=True)

    language_id: int = Field(foreign_key="language.id")
    group_id: int = Field(foreign_key="taskgroup.id", nullable=False, ondelete="CASCADE")
    owner_id: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")

    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    update_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    language: Language = Relationship()
    group: TaskGroup = Relationship()
    owner: User = Relationship()


class WorkNode(SQLModel, table=True):
    """工作节点表"""

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
