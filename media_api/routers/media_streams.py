from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from ..core.database import get_db
from ..core.models import MediaStream, MediaFile
from ..core.schemas import MediaStreamResponse, MediaStreamCreate, MediaStreamUpdate

router = APIRouter(prefix="/media-streams", tags=["media-streams"])


@router.post(
    "/", response_model=MediaStreamResponse, status_code=status.HTTP_201_CREATED
)
async def create_media_stream(
    stream_data: MediaStreamCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MediaFile).where(MediaFile.id == stream_data.media_file_id)
    )
    media_file = result.scalar_one_or_none()

    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found"
        )

    try:
        media_stream = MediaStream(**stream_data.model_dump())
        db.add(media_stream)
        await db.commit()
        await db.refresh(media_stream)
        return media_stream
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating media stream: {str(e)}",
        )


@router.get("/", response_model=List[MediaStreamResponse])
async def list_media_streams(
    skip: int = 0,
    limit: int = 100,
    media_file_id: Optional[int] = None,
    codec_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(MediaStream).offset(skip).limit(limit)

    if media_file_id:
        query = query.where(MediaStream.media_file_id == media_file_id)

    if codec_type:
        query = query.where(MediaStream.codec_type == codec_type)

    query = query.order_by(MediaStream.media_file_id, MediaStream.index)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{stream_id}", response_model=MediaStreamResponse)
async def get_media_stream(stream_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MediaStream).where(MediaStream.id == stream_id))
    media_stream = result.scalar_one_or_none()

    if not media_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Media stream not found"
        )

    return media_stream


@router.put("/{stream_id}", response_model=MediaStreamResponse)
async def update_media_stream(
    stream_id: int, stream_data: MediaStreamUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(MediaStream).where(MediaStream.id == stream_id))
    media_stream = result.scalar_one_or_none()

    if not media_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Media stream not found"
        )

    try:
        update_data = stream_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(media_stream, field, value)

        await db.commit()
        await db.refresh(media_stream)
        return media_stream
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating media stream: {str(e)}",
        )


@router.delete("/{stream_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media_stream(stream_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MediaStream).where(MediaStream.id == stream_id))
    media_stream = result.scalar_one_or_none()

    if not media_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Media stream not found"
        )

    try:
        await db.delete(media_stream)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting media stream: {str(e)}",
        )


@router.get("/by-type/{codec_type}", response_model=List[MediaStreamResponse])
async def get_streams_by_type(
    codec_type: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MediaStream)
        .where(MediaStream.codec_type == codec_type)
        .offset(skip)
        .limit(limit)
        .order_by(MediaStream.media_file_id, MediaStream.index)
    )
    return result.scalars().all()
