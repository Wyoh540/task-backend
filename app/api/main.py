from fastapi import APIRouter

from app.api.routes import jobs, users, login, language, worker

api_router = APIRouter()

api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(jobs.router)
api_router.include_router(language.router)
api_router.include_router(worker.router)
