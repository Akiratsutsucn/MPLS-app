from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.reminder import Reminder
from app.models.project import Project
from app.models.user import User
from app.schemas.reminder import ReminderCreate, ReminderResponse
from app.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["reminders"])


async def _get_project_or_404(project_id: int, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/reminders", response_model=list[ReminderResponse])
async def list_reminders(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_project_or_404(project_id, db)

    result = await db.execute(
        select(Reminder)
        .where(Reminder.project_id == project_id)
        .order_by(Reminder.remind_date.asc())
    )
    return result.scalars().all()


@router.post("/{project_id}/reminders", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def add_reminder(
    project_id: int,
    payload: ReminderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_project_or_404(project_id, db)

    reminder = Reminder(
        project_id=project_id,
        title=payload.title,
        remind_date=payload.remind_date,
        created_by=current_user.id,
    )
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder


@router.delete("/{project_id}/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    project_id: int,
    reminder_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.project_id == project_id,
        )
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    await db.delete(reminder)
    await db.commit()
