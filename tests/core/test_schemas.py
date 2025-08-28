import pytest
from datetime import datetime
from media_api.core.schemas import (
    FFProbeDisposition,
    FFProbeStream,
    FFProbeChapter,
    FFProbeFormat,
    FFProbeOutput,
    MediaStreamResponse,
    MediaChapterResponse,
    MediaFileResponse,
)


class TestFFProbeSchemas:
    def test_ffprobe_disposition_defaults(self):
        disposition = FFProbeDisposition()
        assert disposition.default == 0
        assert disposition.dub == 0
        assert disposition.forced == 0

    def test_ffprobe_disposition_with_values(self):
        disposition = FFProbeDisposition(default=1, forced=1)
        assert disposition.default == 1
        assert disposition.forced == 1
        assert disposition.dub == 0

    def test_ffprobe_stream_minimal(self):
        stream = FFProbeStream(index=0)
        assert stream.index == 0
        assert stream.codec_name is None
        assert stream.width is None

    def test_ffprobe_stream_video(self):
        stream = FFProbeStream(
            index=0,
            codec_name="h264",
            codec_type="video",
            width=1920,
            height=1080,
            duration="120.5",
            bit_rate="5000000",
        )
        assert stream.index == 0
        assert stream.codec_name == "h264"
        assert stream.width == 1920
        assert stream.height == 1080
        assert stream.duration == "120.5"

    def test_ffprobe_stream_audio(self):
        stream = FFProbeStream(
            index=1,
            codec_name="aac",
            codec_type="audio",
            sample_rate=44100,
            channels=2,
            channel_layout="stereo",
        )
        assert stream.codec_name == "aac"
        assert stream.sample_rate == 44100
        assert stream.channels == 2
        assert stream.channel_layout == "stereo"

    def test_ffprobe_chapter(self):
        chapter = FFProbeChapter(
            id=0,
            time_base="1/1000",
            start=0,
            start_time="0.000000",
            end=60000,
            end_time="60.000000",
            tags={"title": "Chapter 1"},
        )
        assert chapter.id == 0
        assert chapter.start_time == "0.000000"
        assert chapter.tags["title"] == "Chapter 1"

    def test_ffprobe_format(self):
        format_info = FFProbeFormat(
            filename="test.mp4",
            nb_streams=2,
            format_name="mov,mp4,m4a,3gp,3g2,mj2",
            format_long_name="QuickTime / MOV",
            duration="120.5",
            size="10485760",
            bit_rate="696320",
        )
        assert format_info.filename == "test.mp4"
        assert format_info.nb_streams == 2
        assert format_info.duration == "120.5"

    def test_ffprobe_output_complete(self):
        stream = FFProbeStream(index=0, codec_name="h264")
        chapter = FFProbeChapter(id=0, start_time="0.0")
        format_info = FFProbeFormat(filename="test.mp4")

        output = FFProbeOutput(streams=[stream], chapters=[chapter], format=format_info)

        assert len(output.streams) == 1
        assert len(output.chapters) == 1
        assert output.format.filename == "test.mp4"

    def test_ffprobe_output_empty(self):
        output = FFProbeOutput()
        assert output.streams == []
        assert output.chapters == []
        assert output.format is None


class TestResponseSchemas:
    def test_media_stream_response(self):
        stream_data = {
            "id": 1,
            "index": 0,
            "codec_name": "h264",
            "codec_type": "video",
            "width": 1920,
            "height": 1080,
            "duration": 120.5,
            "bit_rate": 5000000,
        }

        response = MediaStreamResponse(**stream_data)
        assert response.id == 1
        assert response.codec_name == "h264"
        assert response.width == 1920

    def test_media_chapter_response(self):
        chapter_data = {
            "id": 1,
            "chapter_id": 0,
            "start_time": 0.0,
            "end_time": 60.0,
            "tags": {"title": "Chapter 1"},
        }

        response = MediaChapterResponse(**chapter_data)
        assert response.id == 1
        assert response.chapter_id == 0
        assert response.tags["title"] == "Chapter 1"

    def test_media_file_response(self):
        file_data = {
            "id": 1,
            "filename": "test.mp4",
            "filepath": "/path/to/test.mp4",
            "file_size": 10485760,
            "format_name": "mp4",
            "duration": 120.5,
            "created_at": datetime.now(),
            "streams": [],
            "chapters": [],
        }

        response = MediaFileResponse(**file_data)
        assert response.id == 1
        assert response.filename == "test.mp4"
        assert response.duration == 120.5
        assert isinstance(response.streams, list)
        assert isinstance(response.chapters, list)
