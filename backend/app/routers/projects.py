from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.project import Project
from app.models.checklist import ChecklistItem
from app.models.log import ProjectLog
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, PhaseUpdate, ProjectResponse, ProjectListResponse
from app.auth import get_current_user
from app.seed import create_default_checklist

router = APIRouter(prefix="/projects", tags=["projects"])


def _compute_completion(items: list[ChecklistItem]) -> float:
    if not items:
        return 0.0
    completed = sum(1 for i in items if i.is_completed)
    return round(completed / len(items) * 100, 1)


def _build_project_response(project: Project, completion: float) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        system_name=project.system_name,
        level=project.level,
        phase=project.phase,
        assignee_id=project.assignee_id,
        assignee_name=project.assignee.name if project.assignee else None,
        client_org=project.client_org,
        deadline=project.deadline,
        notes=project.notes,
        created_by=project.created_by,
        creator_name=project.creator.name if project.creator else None,
        created_at=project.created_at,
        updated_at=project.updated_at,
        checklist_completion=completion,
    )


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    phase: Optional[str] = Query(None),
    assignee_id: Optional[int] = Query(None),
    sort: Optional[str] = Query("created_at", pattern="^(deadline|created_at)$"),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Project)
        .options(
            selectinload(Project.assignee),
            selectinload(Project.creator),
            selectinload(Project.checklist_items),
        )
    )
    if phase:
        stmt = stmt.where(Project.phase == phase)
    if assignee_id:
        stmt = stmt.where(Project.assignee_id == assignee_id)

    sort_col = Project.deadline if sort == "deadline" else Project.created_at
    stmt = stmt.order_by(sort_col.asc() if order == "asc" else sort_col.desc())

    result = await db.execute(stmt)
    projects = result.scalars().all()

    items = [_build_project_response(p, _compute_completion(p.checklist_items)) for p in projects]
    return ProjectListResponse(items=items, total=len(items))


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(
        name=payload.name,
        system_name=payload.system_name,
        level=payload.level,
        assignee_id=payload.assignee_id,
        client_org=payload.client_org or "",
        deadline=payload.deadline,
        notes=payload.notes or "",
        created_by=current_user.id,
    )
    db.add(project)
    await db.flush()

    checklist_items = create_default_checklist(project.id)
    for item in checklist_items:
        db.add(item)

    log = ProjectLog(
        project_id=project.id,
        content="项目创建",
        log_type="system",
        created_by=current_user.id,
    )
    db.add(log)
    await db.commit()

    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.assignee),
            selectinload(Project.creator),
            selectinload(Project.checklist_items),
        )
        .where(Project.id == project.id)
    )
    project = result.scalar_one()
    return _build_project_response(project, _compute_completion(project.checklist_items))


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.assignee),
            selectinload(Project.creator),
            selectinload(Project.checklist_items),
        )
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return _build_project_response(project, _compute_completion(project.checklist_items))


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.assignee),
            selectinload(Project.creator),
            selectinload(Project.checklist_items),
        )
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)

    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.assignee),
            selectinload(Project.creator),
            selectinload(Project.checklist_items),
        )
        .where(Project.id == project_id)
    )
    project = result.scalar_one()
    return _build_project_response(project, _compute_completion(project.checklist_items))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.commit()


@router.patch("/{project_id}/phase", response_model=ProjectResponse)
async def update_phase(
    project_id: int,
    payload: PhaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.assignee),
            selectinload(Project.creator),
            selectinload(Project.checklist_items),
        )
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    old_phase = project.phase
    project.phase = payload.phase

    log = ProjectLog(
        project_id=project.id,
        content=f"阶段变更: {old_phase} → {payload.phase}",
        log_type="system",
        created_by=current_user.id,
    )
    db.add(log)
    await db.commit()

    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.assignee),
            selectinload(Project.creator),
            selectinload(Project.checklist_items),
        )
        .where(Project.id == project_id)
    )
    project = result.scalar_one()
    return _build_project_response(project, _compute_completion(project.checklist_items))
