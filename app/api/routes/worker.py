import psutil
import datetime

from fastapi import APIRouter
from celery.app.control import Inspect

from app.celery import celery_app

router = APIRouter(prefix="/worker", tags=["Worker"])


@router.get("/")
def list_worker() -> dict:

    timeout = 2.0

    inspect = Inspect(app=celery_app)

    workers = inspect.ping() or {}
    if not workers:
        return {}

    # 获取详细统计信息
    stats = inspect.stats() or {}

    # 获取注册的任务列表
    registered_tasks = inspect.registered() or {}

    # 获取活跃任务
    active_tasks = inspect.active() or {}

    # 组装完整信息
    result = {}
    for worker_id in workers.keys():
        # 基础信息
        info = {
            "worker_id": worker_id,
            "last_ping": datetime.datetime.now().isoformat(),
            "status": "online" if worker_id in stats else "offline",
            "node_info": stats.get(worker_id, {}).get("node", {}),
            "system": _get_system_info(worker_id),
        }

        # 合并统计信息
        if worker_id in stats:
            info.update(
                {
                    "concurrency": stats[worker_id].get("pool", {}).get("max-concurrency"),
                    "running_tasks": len(active_tasks.get(worker_id, [])),
                    "registered_tasks": registered_tasks.get(worker_id, []),
                    "total_tasks": stats[worker_id].get("total", {}),
                    "broker": _get_broker_info(stats[worker_id]),
                }
            )

        # 添加进程信息（本地 worker 才可获取）
        if worker_id.endswith("@" + psutil.Process().name()):
            info["process"] = _get_process_info()

        result[worker_id] = info

    return result


def _get_system_info(worker_id: str) -> dict:
    """获取系统级信息（示例）"""
    return {
        "platform": psutil.sys.platform,
        "cpu_count": psutil.cpu_count(),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage("/")._asdict(),
        "hostname": psutil.Process().name(),
    }


def _get_broker_info(stats: dict) -> dict:
    """解析 broker 信息"""
    transport = stats.get("transport", "")
    if "redis" in transport.lower():
        return {"type": "redis", "host": transport.split("//")[1].split("/")[0]}
    elif "amqp" in transport.lower():
        return {"type": "rabbitmq", "host": transport.split("@")[1].split("/")[0]}
    return {"type": "unknown"}


def _get_process_info() -> dict:
    """获取本地 worker 进程信息"""
    proc = psutil.Process()
    return {
        "pid": proc.pid,
        "cpu_percent": proc.cpu_percent(),
        "memory_mb": proc.memory_info().rss // 1024 // 1024,
        "open_files": len(proc.open_files()),
        "connections": [c._asdict() for c in proc.connections()],
    }
