from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta, date
from typing import Optional

from app.database import get_db
from app.models.project import Project
from app.models.reminder import Reminder
from app.models.checklist import ChecklistItem
from app.models.user import User
from app.schemas.project import ProjectResponse
from app.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


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


@router.get("/upcoming", response_model=list[ProjectResponse])
async def upcoming(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    cutoff_dt = now + timedelta(days=7)
    cutoff_date = (date.today() + timedelta(days=7))

    # Projects with deadline within 7 days
    deadline_stmt = (
        select(Project)
        .options(
            selectinload(Project.assignee),
            selectinload(Project.creator),
            selectinload(Project.checklist_items),
        )
        .where(
            and_(
                Project.deadline.is_not(None),
                Project.deadline >= now,
                Project.deadline <= cutoff_dt,
            )
        )
    )
    deadline_result = await db.execute(deadline_stmt)
    deadline_projects = {p.id: p for p in deadline_result.scalars().all()}

    # Projects with reminders within 7 days
    reminder_stmt = (
        select(Reminder.project_id)
        .where(
            and_(
                Reminder.is_dismissed == False,
                Reminder.remind_date >= date.today(),
                Reminder.remind_date <= cutoff_date,
            )
        )
        .distinct()
    )
    reminder_result = await db.execute(reminder_stmt)
    reminder_project_ids = {row[0] for row in reminder_result.all()}

    # Load reminder projects not already in deadline set
    missing_ids = reminder_project_ids - set(deadline_projects.keys())
    if missing_ids:
        reminder_projects_stmt = (
            select(Project)
            .options(
                selectinload(Project.assignee),
                selectinload(Project.creator),
                selectinload(Project.checklist_items),
            )
            .where(Project.id.in_(missing_ids))
        )
        rp_result = await db.execute(reminder_projects_stmt)
        for p in rp_result.scalars().all():
            deadline_projects[p.id] = p

    projects = sorted(
        deadline_projects.values(),
        key=lambda p: p.deadline or datetime.max,
    )

    return [_build_project_response(p, _compute_completion(p.checklist_items)) for p in projects]
