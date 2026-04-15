from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.log import ProjectLog
from app.models.project import Project
from app.models.user import User
from app.schemas.log import LogCreate, LogResponse
from app.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["logs"])


async def _get_project_or_404(project_id: int, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _to_log_response(log: ProjectLog) -> LogResponse:
    return LogResponse(
        id=log.id,
        project_id=log.project_id,
        content=log.content,
        log_type=log.log_type,
        created_by=log.created_by,
        author_name=log.author.name if log.author else None,
        created_at=log.created_at,
    )


@router.get("/{project_id}/logs", response_model=list[LogResponse])
async def list_logs(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_project_or_404(project_id, db)

    result = await db.execute(
        select(ProjectLog)
        .options(selectinload(ProjectLog.author))
        .where(ProjectLog.project_id == project_id)
        .order_by(ProjectLog.created_at.desc())
    )
    logs = result.scalars().all()
    return [_to_log_response(log) for log in logs]


@router.post("/{project_id}/logs", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def add_log(
    project_id: int,
    payload: LogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_project_or_404(project_id, db)

    log = ProjectLog(
        project_id=project_id,
        content=payload.content,
        log_type="manual",
        created_by=current_user.id,
    )
    db.add(log)
    await db.commit()

    result = await db.execute(
        select(ProjectLog)
        .options(selectinload(ProjectLog.author))
        .where(ProjectLog.id == log.id)
    )
    log = result.scalar_one()
    return _to_log_response(log)
