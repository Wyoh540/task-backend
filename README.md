# FastAPI 示例工程

## 核心依赖

* [Pydantic](https://docs.pydantic.dev/2.10/)
* [SQLModel](https://sqlmodel.fastapi.org.cn/)
* [Alembic](https://alembic.sqlalchemy.org/en/latest/)
* [Celery](https://docs.celeryq.dev/en/stable/index.html)

## 数据库

生成迁移数据

```bash
alembic revision --autogenerate -m "init db"
```

更新迁移

```bash
alembic upgrade head
```

## 工程启动

启动celery worker

```bash
celery -A app.celery worker -p solo --concurrency=2  --loglevel=INFO
```
