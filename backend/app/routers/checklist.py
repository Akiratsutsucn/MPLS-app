from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.checklist import ChecklistItem
from app.models.project import Project
from app.models.user import User
from app.schemas.checklist import ChecklistItemCreate, ChecklistItemUpdate, ChecklistItemResponse
from app.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["checklist"])


async def _get_project_or_404(project_id: int, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/checklist", response_model=list[ChecklistItemResponse])
async def list_checklist(
    project_id: int,
    phase: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_project_or_404(project_id, db)

    stmt = select(ChecklistItem).where(ChecklistItem.project_id == project_id)
    if phase:
        stmt = stmt.where(ChecklistItem.phase == phase)
    stmt = stmt.order_by(ChecklistItem.phase, ChecklistItem.sort_order)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{project_id}/checklist", response_model=ChecklistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_checklist_item(
    project_id: int,
    payload: ChecklistItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_project_or_404(project_id, db)

    result = await db.execute(
        select(ChecklistItem)
        .where(ChecklistItem.project_id == project_id, ChecklistItem.phase == payload.phase)
        .order_by(ChecklistItem.sort_order.desc())
    )
    last = result.scalars().first()
    next_order = (last.sort_order + 1) if last else 0

    item = ChecklistItem(
        project_id=project_id,
        phase=payload.phase,
        content=payload.content,
        sort_order=next_order,
        is_custom=True,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/{project_id}/checklist/{item_id}", response_model=ChecklistItemResponse)
async def toggle_checklist_item(
    project_id: int,
    item_id: int,
    payload: ChecklistItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChecklistItem).where(
            ChecklistItem.id == item_id,
            ChecklistItem.project_id == project_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    if payload.content is not None:
        item.content = payload.content

    if payload.is_completed is not None:
        item.is_completed = payload.is_completed
        if payload.is_completed:
            item.completed_at = datetime.utcnow()
            item.completed_by = current_user.id
        else:
            item.completed_at = None
            item.completed_by = None

    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{project_id}/checklist/{item_id}", response_model=ChecklistItemResponse)
async def update_checklist_item(
    project_id: int,
    item_id: int,
    payload: ChecklistItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChecklistItem).where(
            ChecklistItem.id == item_id,
            ChecklistItem.project_id == project_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    item.content = payload.content
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{project_id}/checklist/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist_item(
    project_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChecklistItem).where(
            ChecklistItem.id == item_id,
            ChecklistItem.project_id == project_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    await db.delete(item)
    await db.commit()
