from sqlmodel import Session, select

from app.models.task import Task, TaskGroup, WorkNode
from app.schemas.task import TaskCreate, TaskGroupCreate, WorkNodeCreate


class TaskService:
    """任务管理"""

    @classmethod
    def create_group(cls, db: Session, group_create: TaskGroupCreate) -> TaskGroup:
        group = db.exec(select(TaskGroup).where(TaskGroup.name == group_create.name)).first()
        if not group:
            group = TaskGroup.model_validate(group_create)
            db.add(group)
            db.commit()
            db.refresh(group)

        return group

    @classmethod
    def create_task(cls, db: Session, task_create: TaskCreate, group_id: int, user_id: int) -> Task:
        """创建任务"""
        task = db.exec(
            select(Task).where(Task.task_name == task_create.task_name, Task.group_id == group_id)
        ).first()
        if not task:
            task = Task.model_validate(task_create, update={"group_id": group_id, "owner_id": user_id})
            db.add(task)
            db.commit()
            db.refresh(task)
        return task


class WorkNodeService:
    """工作节点管理"""

    @classmethod
    def create_node(cls, db: Session, node_create: WorkNodeCreate) -> WorkNode:
        node = db.exec(
            select(WorkNode).where(WorkNode.node_ip == node_create.node_ip)
        )
        if not node.first():
            node = WorkNode.model_validate(node_create)
            db.add(node)
            db.commit()
            db.refresh(node)
        return node

    @classmethod
    def update_node(cls, db: Session, node_id: int, node_update) -> None:
        # Placeholder for updating a work node
        pass

    @classmethod
    def delete_node(cls, db: Session, node_id: int) -> None:
        # Placeholder for deleting a work node
        pass