from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import *  # noqa: F401, F403 - ensure all models registered
from app.routers import auth, projects, checklist, documents, logs, reminders, dashboard, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="等级保护项目管理", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api", tags=["认证"])
app.include_router(projects.router, prefix="/api", tags=["项目"])
app.include_router(checklist.router, prefix="/api", tags=["检查清单"])
app.include_router(documents.router, prefix="/api", tags=["文档"])
app.include_router(logs.router, prefix="/api", tags=["日志"])
app.include_router(reminders.router, prefix="/api", tags=["提醒"])
app.include_router(dashboard.router, prefix="/api", tags=["仪表盘"])
app.include_router(export.router, prefix="/api", tags=["导出"])
