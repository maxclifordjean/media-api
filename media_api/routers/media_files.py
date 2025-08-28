from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from ..core.database import get_db
from ..core.models import MediaFile, MediaStream, MediaChapter
from ..core.schemas import MediaFileResponse, MediaFileCreate
from ..utils.ffprobe_parser import FFProbeParser

router = APIRouter(prefix="/media-files", tags=["media-files"])


@router.post("/", response_model=MediaFileResponse, status_code=status.HTTP_201_CREATED)
async def create_media_file(
    media_file_data: MediaFileCreate, db: AsyncSession = Depends(get_db)
):
    try:
        media_file = FFProbeParser.parse_ffprobe_to_models(
            media_file_data.filepath, media_file_data.ffprobe_data.model_dump()
        )
        db.add(media_file)
        await db.commit()
        await db.refresh(media_file)

        result = await db.execute(
            select(MediaFile)
            .options(selectinload(MediaFile.streams), selectinload(MediaFile.chapters))
            .where(MediaFile.id == media_file.id)
        )
        return result.scalar_one()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating media file: {str(e)}",
        )


@router.get("/", response_model=List[MediaFileResponse])
async def list_media_files(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MediaFile)
        .options(selectinload(MediaFile.streams), selectinload(MediaFile.chapters))
        .offset(skip)
        .limit(limit)
        .order_by(MediaFile.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{media_file_id}", response_model=MediaFileResponse)
async def get_media_file(media_file_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MediaFile)
        .options(selectinload(MediaFile.streams), selectinload(MediaFile.chapters))
        .where(MediaFile.id == media_file_id)
    )
    media_file = result.scalar_one_or_none()

    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found"
        )

    return media_file


@router.put("/{media_file_id}", response_model=MediaFileResponse)
async def update_media_file(
    media_file_id: int,
    media_file_data: MediaFileCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(MediaFile).where(MediaFile.id == media_file_id))
    existing_media_file = result.scalar_one_or_none()

    if not existing_media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found"
        )

    try:
        await db.delete(existing_media_file)

        updated_media_file = FFProbeParser.parse_ffprobe_to_models(
            media_file_data.filepath, media_file_data.ffprobe_data.model_dump()
        )
        updated_media_file.id = media_file_id

        db.add(updated_media_file)
        await db.commit()
        await db.refresh(updated_media_file)

        result = await db.execute(
            select(MediaFile)
            .options(selectinload(MediaFile.streams), selectinload(MediaFile.chapters))
            .where(MediaFile.id == updated_media_file.id)
        )
        return result.scalar_one()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating media file: {str(e)}",
        )


@router.delete("/{media_file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media_file(media_file_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MediaFile).where(MediaFile.id == media_file_id))
    media_file = result.scalar_one_or_none()

    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found"
        )

    try:
        await db.delete(media_file)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting media file: {str(e)}",
        )


@router.get("/{media_file_id}/streams", response_model=List[dict])
async def get_media_file_streams(
    media_file_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MediaFile)
        .options(selectinload(MediaFile.streams))
        .where(MediaFile.id == media_file_id)
    )
    media_file = result.scalar_one_or_none()

    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found"
        )

    return media_file.streams
