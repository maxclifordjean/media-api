import json
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path
from media_api.core.schemas import FFProbeOutput
from media_api.core.models import MediaFile, MediaStream, MediaChapter, FFProbeError
from sqlalchemy.ext.asyncio import AsyncSession


class FFProbeParser:
    @staticmethod
    async def run_ffprobe(filepath: str) -> Optional[Dict[str, Any]]:
        """Run ffprobe on a file and return the JSON output."""
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            "-show_chapters",
            filepath,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                raise subprocess.CalledProcessError(
                    result.returncode, cmd, result.stderr
                )

        except subprocess.TimeoutExpired:
            raise Exception(f"FFprobe timeout for file: {filepath}")
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFprobe failed: {e.stderr}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse ffprobe output: {e}")

    @staticmethod
    def parse_ffprobe_to_models(
        filepath: str, ffprobe_data: Dict[str, Any]
    ) -> MediaFile:
        """Convert ffprobe JSON data to SQLAlchemy models."""
        # Parse the data using Pydantic schema
        parsed_data = FFProbeOutput(**ffprobe_data)

        # Extract file info
        file_path = Path(filepath)
        filename = file_path.name

        # Create MediaFile instance
        media_file = MediaFile(
            filename=filename, filepath=filepath, raw_ffprobe=ffprobe_data
        )

        # Process format information
        if parsed_data.format:
            fmt = parsed_data.format
            media_file.file_size = int(fmt.size) if fmt.size else None
            media_file.format_name = fmt.format_name
            media_file.format_long_name = fmt.format_long_name
            media_file.duration = float(fmt.duration) if fmt.duration else None
            media_file.bit_rate = int(fmt.bit_rate) if fmt.bit_rate else None
            media_file.probe_score = fmt.probe_score
            media_file.start_time = float(fmt.start_time) if fmt.start_time else None
            media_file.nb_streams = fmt.nb_streams
            media_file.nb_programs = fmt.nb_programs
            media_file.tags = fmt.tags

        # Process streams
        if parsed_data.streams:
            for stream_data in parsed_data.streams:
                stream = MediaStream(
                    index=stream_data.index,
                    codec_name=stream_data.codec_name,
                    codec_long_name=stream_data.codec_long_name,
                    codec_type=stream_data.codec_type,
                    codec_tag_string=stream_data.codec_tag_string,
                    codec_tag=stream_data.codec_tag,
                    # Video fields
                    width=stream_data.width,
                    height=stream_data.height,
                    coded_width=stream_data.coded_width,
                    coded_height=stream_data.coded_height,
                    closed_captions=stream_data.closed_captions,
                    film_grain=stream_data.film_grain,
                    has_b_frames=stream_data.has_b_frames,
                    sample_aspect_ratio=stream_data.sample_aspect_ratio,
                    display_aspect_ratio=stream_data.display_aspect_ratio,
                    pix_fmt=stream_data.pix_fmt,
                    level=stream_data.level,
                    color_range=stream_data.color_range,
                    color_space=stream_data.color_space,
                    color_transfer=stream_data.color_transfer,
                    color_primaries=stream_data.color_primaries,
                    chroma_location=stream_data.chroma_location,
                    field_order=stream_data.field_order,
                    refs=stream_data.refs,
                    r_frame_rate=stream_data.r_frame_rate,
                    avg_frame_rate=stream_data.avg_frame_rate,
                    time_base=stream_data.time_base,
                    # Audio fields
                    sample_fmt=stream_data.sample_fmt,
                    sample_rate=stream_data.sample_rate,
                    channels=stream_data.channels,
                    channel_layout=stream_data.channel_layout,
                    bits_per_sample=stream_data.bits_per_sample,
                    # Common fields
                    start_pts=stream_data.start_pts,
                    start_time=float(stream_data.start_time)
                    if stream_data.start_time
                    else None,
                    duration_ts=stream_data.duration_ts,
                    duration=float(stream_data.duration)
                    if stream_data.duration
                    else None,
                    bit_rate=int(stream_data.bit_rate)
                    if stream_data.bit_rate
                    else None,
                    max_bit_rate=int(stream_data.max_bit_rate)
                    if stream_data.max_bit_rate
                    else None,
                    bits_per_raw_sample=stream_data.bits_per_raw_sample,
                    nb_frames=int(stream_data.nb_frames)
                    if stream_data.nb_frames
                    else None,
                    nb_read_frames=int(stream_data.nb_read_frames)
                    if stream_data.nb_read_frames
                    else None,
                    nb_read_packets=int(stream_data.nb_read_packets)
                    if stream_data.nb_read_packets
                    else None,
                    disposition=stream_data.disposition.model_dump()
                    if stream_data.disposition
                    else None,
                    tags=stream_data.tags,
                )
                media_file.streams.append(stream)

        # Process chapters
        if parsed_data.chapters:
            for chapter_data in parsed_data.chapters:
                chapter = MediaChapter(
                    chapter_id=chapter_data.id,
                    time_base=chapter_data.time_base,
                    start=chapter_data.start,
                    start_time=float(chapter_data.start_time)
                    if chapter_data.start_time
                    else None,
                    end=chapter_data.end,
                    end_time=float(chapter_data.end_time)
                    if chapter_data.end_time
                    else None,
                    tags=chapter_data.tags,
                )
                media_file.chapters.append(chapter)

        return media_file

    @staticmethod
    async def process_media_file(
        db: AsyncSession, filepath: str
    ) -> Optional[MediaFile]:
        """Process a media file with ffprobe and save to database."""
        try:
            # Run ffprobe
            ffprobe_data = await FFProbeParser.run_ffprobe(filepath)
            if not ffprobe_data:
                return None

            # Parse to models
            media_file = FFProbeParser.parse_ffprobe_to_models(filepath, ffprobe_data)

            # Save to database
            db.add(media_file)
            await db.commit()
            await db.refresh(media_file)

            return media_file

        except Exception as e:
            # Log error to database
            error_record = FFProbeError(
                filepath=filepath,
                error_message=str(e),
                error_code=getattr(e, "returncode", -1),
            )
            db.add(error_record)
            await db.commit()

            raise e
