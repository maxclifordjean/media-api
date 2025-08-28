import pytest
import json
import subprocess
from unittest.mock import patch, MagicMock, AsyncMock
from media_api.utils.ffprobe_parser import FFProbeParser
from media_api.core.models import MediaFile, MediaStream, MediaChapter, FFProbeError


class TestFFProbeParser:
    @pytest.mark.asyncio
    async def test_run_ffprobe_success(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"format": {"filename": "test.mp4"}}'

        with patch("subprocess.run", return_value=mock_result):
            result = await FFProbeParser.run_ffprobe("/path/to/test.mp4")

            assert result is not None
            assert result["format"]["filename"] == "test.mp4"

    @pytest.mark.asyncio
    async def test_run_ffprobe_command_error(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "No such file or directory"

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(Exception) as exc_info:
                await FFProbeParser.run_ffprobe("/invalid/path.mp4")

            assert "FFprobe failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_run_ffprobe_timeout(self):
        with patch(
            "subprocess.run", side_effect=subprocess.TimeoutExpired("ffprobe", 60)
        ):
            with pytest.raises(Exception) as exc_info:
                await FFProbeParser.run_ffprobe("/path/to/test.mp4")

            assert "FFprobe timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_run_ffprobe_json_decode_error(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid json"

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(Exception) as exc_info:
                await FFProbeParser.run_ffprobe("/path/to/test.mp4")

            assert "Failed to parse ffprobe output" in str(exc_info.value)

    def test_parse_ffprobe_to_models_basic(self):
        ffprobe_data = {
            "format": {
                "filename": "/path/to/test.mp4",
                "size": "1048576",
                "duration": "120.5",
                "bit_rate": "1000000",
                "format_name": "mp4",
                "format_long_name": "MP4 (MPEG-4 Part 14)",
                "nb_streams": 2,
                "tags": {"title": "Test Video"},
            },
            "streams": [
                {
                    "index": 0,
                    "codec_name": "h264",
                    "codec_type": "video",
                    "width": 1920,
                    "height": 1080,
                    "duration": "120.5",
                    "bit_rate": "5000000",
                    "tags": {"language": "eng"},
                }
            ],
            "chapters": [
                {
                    "id": 0,
                    "start_time": "0.0",
                    "end_time": "60.0",
                    "tags": {"title": "Chapter 1"},
                }
            ],
        }

        media_file = FFProbeParser.parse_ffprobe_to_models(
            "/path/to/test.mp4", ffprobe_data
        )

        assert isinstance(media_file, MediaFile)
        assert media_file.filename == "test.mp4"
        assert media_file.filepath == "/path/to/test.mp4"
        assert media_file.file_size == 1048576
        assert media_file.duration == 120.5
        assert media_file.format_name == "mp4"
        assert media_file.tags["title"] == "Test Video"

        assert len(media_file.streams) == 1
        stream = media_file.streams[0]
        assert stream.index == 0
        assert stream.codec_name == "h264"
        assert stream.codec_type == "video"
        assert stream.width == 1920
        assert stream.height == 1080

        assert len(media_file.chapters) == 1
        chapter = media_file.chapters[0]
        assert chapter.chapter_id == 0
        assert chapter.start_time == 0.0
        assert chapter.end_time == 60.0

    def test_parse_ffprobe_to_models_minimal(self):
        ffprobe_data = {"format": {"filename": "/path/to/test.mp4"}}

        media_file = FFProbeParser.parse_ffprobe_to_models(
            "/path/to/test.mp4", ffprobe_data
        )

        assert media_file.filename == "test.mp4"
        assert media_file.filepath == "/path/to/test.mp4"
        assert media_file.file_size is None
        assert media_file.duration is None
        assert len(media_file.streams) == 0
        assert len(media_file.chapters) == 0

    def test_parse_ffprobe_audio_stream(self):
        ffprobe_data = {
            "format": {"filename": "/path/to/test.mp4"},
            "streams": [
                {
                    "index": 0,
                    "codec_name": "aac",
                    "codec_type": "audio",
                    "sample_rate": 44100,
                    "channels": 2,
                    "channel_layout": "stereo",
                    "duration": "120.0",
                    "bit_rate": "128000",
                }
            ],
        }

        media_file = FFProbeParser.parse_ffprobe_to_models(
            "/path/to/test.mp4", ffprobe_data
        )

        assert len(media_file.streams) == 1
        stream = media_file.streams[0]
        assert stream.codec_name == "aac"
        assert stream.codec_type == "audio"
        assert stream.sample_rate == 44100
        assert stream.channels == 2
        assert stream.channel_layout == "stereo"

    @pytest.mark.asyncio
    async def test_process_media_file_success(self, db_session):
        ffprobe_data = {
            "format": {"filename": "/path/to/test.mp4", "duration": "120.0"}
        }

        with patch.object(FFProbeParser, "run_ffprobe", return_value=ffprobe_data):
            media_file = await FFProbeParser.process_media_file(
                db_session, "/path/to/test.mp4"
            )

            assert isinstance(media_file, MediaFile)
            assert media_file.filename == "test.mp4"
            assert media_file.duration == 120.0
            assert media_file.id is not None

    @pytest.mark.asyncio
    async def test_process_media_file_ffprobe_failure(self, db_session):
        with patch.object(
            FFProbeParser, "run_ffprobe", side_effect=Exception("FFprobe failed")
        ):
            with pytest.raises(Exception):
                await FFProbeParser.process_media_file(db_session, "/path/to/test.mp4")

            await db_session.commit()

            from sqlalchemy import select

            result = await db_session.execute(select(FFProbeError))
            error_records = result.scalars().all()

            assert len(error_records) == 1
            error = error_records[0]
            assert error.filepath == "/path/to/test.mp4"
            assert "FFprobe failed" in error.error_message

    @pytest.mark.asyncio
    async def test_process_media_file_no_data(self, db_session):
        with patch.object(FFProbeParser, "run_ffprobe", return_value=None):
            result = await FFProbeParser.process_media_file(
                db_session, "/path/to/test.mp4"
            )
            assert result is None
