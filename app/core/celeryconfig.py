"""Celery 配置"""

# 任务序列化方式
task_serializer = "json"

# 结果序列化方式
result_serializer = "json"
accept_content = ["json"]

# 时区
timezone = "Asia/Shanghai"
enable_utc = True
