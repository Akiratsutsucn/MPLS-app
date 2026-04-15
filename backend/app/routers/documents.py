import os
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.document import Document
from app.models.project import Project
from app.models.log import ProjectLog
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.auth import get_current_user
from app.config import get_settings

router = APIRouter(prefix="/projects", tags=["documents"])


async def _get_project_or_404(project_id: int, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    settings = get_settings()
    project = await _get_project_or_404(project_id, db)

    save_dir = os.path.join(settings.UPLOAD_DIR, str(project_id), project.phase)
    os.makedirs(save_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(save_dir, unique_name)

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    with open(filepath, "wb") as f:
        f.write(content)

    doc = Document(
        project_id=project_id,
        phase=project.phase,
        filename=file.filename or unique_name,
        filepath=filepath,
        filesize=len(content),
        uploaded_by=current_user.id,
    )
    db.add(doc)

    log = ProjectLog(
        project_id=project_id,
        content=f"上传文件: {file.filename}",
        log_type="system",
        created_by=current_user.id,
    )
    db.add(log)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.get("/{project_id}/documents", response_model=list[DocumentResponse])
async def list_documents(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_project_or_404(project_id, db)

    result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.uploaded_at.desc())
    )
    return result.scalars().all()


@router.get("/{project_id}/documents/{doc_id}/download")
async def download_document(
    project_id: int,
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.project_id == project_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not os.path.exists(doc.filepath):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=doc.filepath,
        filename=doc.filename,
        media_type="application/octet-stream",
    )


@router.delete("/{project_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    project_id: int,
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.project_id == project_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if os.path.exists(doc.filepath):
        os.remove(doc.filepath)

    await db.delete(doc)
    await db.commit()
