from sqlmodel import Session, select

from app.models.job import Job, Team, WorkNode
from app.schemas.job import JobCreate, TeamCreate, WorkNodeCreate


class JobService:
    """任务管理"""

    @classmethod
    def create_team(cls, db: Session, team_create: TeamCreate) -> Team:
        team = db.exec(select(Team).where(Team.name == team_create.name)).first()
        if not team:
            team = Team.model_validate(team_create)
            db.add(team)
            db.commit()
            db.refresh(team)

        return team

    @classmethod
    def create_job(cls, db: Session, job_create: JobCreate, team_id: int, user_id: int) -> Job:
        """创建任务"""
        job = db.exec(select(Job).where(Job.name == job_create.name, Job.team_id == team_id)).first()
        if not job:
            job = Job.model_validate(job_create, update={"team_id": team_id, "owner_id": user_id})
            db.add(job)
            db.commit()
            db.refresh(job)
        return job


class WorkNodeService:
    """工作节点管理"""

    @classmethod
    def create_node(cls, db: Session, node_create: WorkNodeCreate) -> WorkNode:
        node = db.exec(select(WorkNode).where(WorkNode.node_ip == node_create.node_ip))
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
