import pytest
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from media_api.core.models import MediaFile, MediaStream, MediaChapter, FFProbeError


@pytest.mark.asyncio
class TestMediaFile:
    async def test_create_media_file(self, db_session):
        media_file = MediaFile(
            filename="test.mp4",
            filepath="/path/to/test.mp4",
            file_size=1024,
            format_name="mp4",
            format_long_name="MP4 (MPEG-4 Part 14)",
            duration=120.5,
            bit_rate=1000,
            nb_streams=2,
            tags={"title": "Test Video"},
        )

        db_session.add(media_file)
        await db_session.commit()
        await db_session.refresh(media_file)

        assert media_file.id is not None
        assert media_file.filename == "test.mp4"
        assert media_file.filepath == "/path/to/test.mp4"
        assert media_file.duration == 120.5
        assert media_file.tags["title"] == "Test Video"

    async def test_media_file_repr(self):
        media_file = MediaFile(filename="test.mp4", duration=120.5)
        assert repr(media_file) == "<MediaFile(filename='test.mp4', duration=120.5)>"

    async def test_media_file_with_streams(self, db_session):
        media_file = MediaFile(filename="test.mp4", filepath="/path/to/test.mp4")

        stream = MediaStream(
            index=0, codec_type="video", codec_name="h264", width=1920, height=1080
        )

        media_file.streams.append(stream)

        db_session.add(media_file)
        await db_session.commit()
        await db_session.refresh(media_file)

        # Use explicit query to load streams instead of lazy loading
        result = await db_session.execute(
            select(MediaFile)
            .options(selectinload(MediaFile.streams))
            .where(MediaFile.id == media_file.id)
        )
        media_file_with_streams = result.scalar_one()

        assert len(media_file_with_streams.streams) == 1
        assert media_file_with_streams.streams[0].codec_name == "h264"


@pytest.mark.asyncio
class TestMediaStream:
    async def test_create_video_stream(self, db_session):
        media_file = MediaFile(filename="test.mp4", filepath="/path/to/test.mp4")
        db_session.add(media_file)
        await db_session.flush()

        stream = MediaStream(
            media_file_id=media_file.id,
            index=0,
            codec_name="h264",
            codec_type="video",
            width=1920,
            height=1080,
            duration=120.0,
            bit_rate=5000,
        )

        db_session.add(stream)
        await db_session.commit()
        await db_session.refresh(stream)

        assert stream.id is not None
        assert stream.codec_name == "h264"
        assert stream.codec_type == "video"
        assert stream.width == 1920
        assert stream.height == 1080

    async def test_create_audio_stream(self, db_session):
        media_file = MediaFile(filename="test.mp4", filepath="/path/to/test.mp4")
        db_session.add(media_file)
        await db_session.flush()

        stream = MediaStream(
            media_file_id=media_file.id,
            index=1,
            codec_name="aac",
            codec_type="audio",
            sample_rate=44100,
            channels=2,
            duration=120.0,
        )

        db_session.add(stream)
        await db_session.commit()
        await db_session.refresh(stream)

        assert stream.codec_name == "aac"
        assert stream.codec_type == "audio"
        assert stream.sample_rate == 44100
        assert stream.channels == 2

    async def test_media_stream_repr(self):
        stream = MediaStream(index=0, codec_type="video", codec_name="h264")
        assert (
            repr(stream)
            == "<MediaStream(index=0, codec_type='video', codec_name='h264')>"
        )


@pytest.mark.asyncio
class TestMediaChapter:
    async def test_create_chapter(self, db_session):
        media_file = MediaFile(filename="test.mp4", filepath="/path/to/test.mp4")
        db_session.add(media_file)
        await db_session.flush()

        chapter = MediaChapter(
            media_file_id=media_file.id,
            chapter_id=1,
            start_time=0.0,
            end_time=60.0,
            tags={"title": "Chapter 1"},
        )

        db_session.add(chapter)
        await db_session.commit()
        await db_session.refresh(chapter)

        assert chapter.id is not None
        assert chapter.chapter_id == 1
        assert chapter.start_time == 0.0
        assert chapter.end_time == 60.0
        assert chapter.tags["title"] == "Chapter 1"

    async def test_media_chapter_repr(self):
        chapter = MediaChapter(chapter_id=1, start_time=0.0, end_time=60.0)
        assert repr(chapter) == "<MediaChapter(id=1, start_time=0.0, end_time=60.0)>"


@pytest.mark.asyncio
class TestFFProbeError:
    async def test_create_ffprobe_error(self, db_session):
        error = FFProbeError(
            filepath="/path/to/corrupted.mp4",
            error_message="Invalid data found when processing input",
            error_code=-1094995529,
        )

        db_session.add(error)
        await db_session.commit()
        await db_session.refresh(error)

        assert error.id is not None
        assert error.filepath == "/path/to/corrupted.mp4"
        assert "Invalid data" in error.error_message
        assert error.error_code == -1094995529
        assert error.attempted_at is not None

    async def test_ffprobe_error_repr(self):
        error = FFProbeError(filepath="/path/to/file.mp4", error_code=-1)
        assert (
            repr(error) == "<FFProbeError(filepath='/path/to/file.mp4', error_code=-1)>"
        )
