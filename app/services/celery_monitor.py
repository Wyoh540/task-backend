import threading
import time
from datetime import datetime, timezone

from celery.events import EventReceiver
from celery import Celery
from kombu import Connection

from app.models.task import WorkNode
from app.core.db import engine
from sqlmodel import Session, select


# 内存中的 worker 状态缓存
global_worker_status = {}

def update_worker_in_db(worker_name, info: dict):
    """将 worker 信息存储或更新到数据库"""
    with Session(engine) as session:
        node = session.exec(select(WorkNode).where(WorkNode.node_name == worker_name)).first()
        now = datetime.now(timezone.utc)
        last_ping = info.get('last_ping')
        if isinstance(last_ping, (int, float)):
            last_ping_dt = datetime.fromtimestamp(last_ping, tz=timezone.utc)
        elif isinstance(last_ping, datetime):
            last_ping_dt = last_ping
        else:
            last_ping_dt = now
        if not node:
            node = WorkNode(node_name=worker_name, node_ip=info.get('ip', ''), platform=info.get('platform', ''), status=WorkNode.NodeStatus.ONLINE)
            node.last_ping = last_ping_dt
            node.create_at = now
            node.update_at = now
            session.add(node)
        else:
            node.status = info.get('status', WorkNode.NodeStatus.ONLINE)
            node.platform = info.get('platform', node.platform)
            node.last_ping = last_ping_dt
            node.update_at = now
        session.commit()

def handle_worker_online(event):
    worker = event['hostname']
    info = {
        'ip': event.get('ip', ''),
        'platform': event.get('platform', ''),
        'last_ping': time.time()
    }
    global_worker_status[worker] = info
    update_worker_in_db(worker, info)

def handle_worker_heartbeat(event):
    worker = event['hostname']
    info = global_worker_status.get(worker, {})
    info['last_ping'] = time.time()
    # 可扩展：从 event['sw_sys']、event['loadavg']、event['mem']、event['disk'] 获取更多信息
    global_worker_status[worker] = info
    update_worker_in_db(worker, info)

def handle_worker_offline(event):
    worker = event['hostname']
    info = global_worker_status.get(worker, {})
    info['status'] = WorkNode.NodeStatus.OFFLINE
    update_worker_in_db(worker, info)
    global_worker_status.pop(worker, None)

def handle_task_event(event):
    # 可扩展：记录 worker 正在运行的任务
    pass

def event_handler(event):
    type = event['type']
    if type == 'worker-online':
        handle_worker_online(event)
    elif type == 'worker-heartbeat':
        handle_worker_heartbeat(event)
    elif type == 'worker-offline':
        handle_worker_offline(event)
    elif type.startswith('task-'):
        handle_task_event(event)

def start_celery_monitor(celery_app: Celery):
    def _run():
        with celery_app.connection() as conn:
            recv = EventReceiver(conn, handlers={'*': event_handler}, app=celery_app)
            recv.capture(limit=None, timeout=None, wakeup=True)
    t = threading.Thread(target=_run, daemon=True)
    t.start()

# 在 celery 启动时调用 start_celery_monitor()
