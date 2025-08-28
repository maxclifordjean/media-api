from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any, Union


# FFProbe input schemas (for parsing ffprobe JSON)
class FFProbeDisposition(BaseModel):
    default: Optional[int] = 0
    dub: Optional[int] = 0
    original: Optional[int] = 0
    comment: Optional[int] = 0
    lyrics: Optional[int] = 0
    karaoke: Optional[int] = 0
    forced: Optional[int] = 0
    hearing_impaired: Optional[int] = 0
    visual_impaired: Optional[int] = 0
    clean_effects: Optional[int] = 0
    attached_pic: Optional[int] = 0
    timed_thumbnails: Optional[int] = 0


class FFProbeStream(BaseModel):
    index: int
    codec_name: Optional[str] = None
    codec_long_name: Optional[str] = None
    codec_type: Optional[str] = None
    codec_tag_string: Optional[str] = None
    codec_tag: Optional[str] = None

    # Video fields
    width: Optional[int] = None
    height: Optional[int] = None
    coded_width: Optional[int] = None
    coded_height: Optional[int] = None
    closed_captions: Optional[bool] = None
    film_grain: Optional[bool] = None
    has_b_frames: Optional[int] = None
    sample_aspect_ratio: Optional[str] = None
    display_aspect_ratio: Optional[str] = None
    pix_fmt: Optional[str] = None
    level: Optional[int] = None
    color_range: Optional[str] = None
    color_space: Optional[str] = None
    color_transfer: Optional[str] = None
    color_primaries: Optional[str] = None
    chroma_location: Optional[str] = None
    field_order: Optional[str] = None
    refs: Optional[int] = None
    r_frame_rate: Optional[str] = None
    avg_frame_rate: Optional[str] = None
    time_base: Optional[str] = None

    # Audio fields
    sample_fmt: Optional[str] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    channel_layout: Optional[str] = None
    bits_per_sample: Optional[int] = None

    # Common fields
    start_pts: Optional[int] = None
    start_time: Optional[Union[str, float]] = None
    duration_ts: Optional[int] = None
    duration: Optional[Union[str, float]] = None
    bit_rate: Optional[Union[str, int]] = None
    max_bit_rate: Optional[Union[str, int]] = None
    bits_per_raw_sample: Optional[int] = None
    nb_frames: Optional[Union[str, int]] = None
    nb_read_frames: Optional[Union[str, int]] = None
    nb_read_packets: Optional[Union[str, int]] = None

    disposition: Optional[FFProbeDisposition] = None
    tags: Optional[Dict[str, Any]] = None


class FFProbeChapter(BaseModel):
    id: int
    time_base: Optional[str] = None
    start: Optional[int] = None
    start_time: Optional[Union[str, float]] = None
    end: Optional[int] = None
    end_time: Optional[Union[str, float]] = None
    tags: Optional[Dict[str, Any]] = None


class FFProbeFormat(BaseModel):
    filename: Optional[str] = None
    nb_streams: Optional[int] = None
    nb_programs: Optional[int] = None
    format_name: Optional[str] = None
    format_long_name: Optional[str] = None
    start_time: Optional[Union[str, float]] = None
    duration: Optional[Union[str, float]] = None
    size: Optional[Union[str, int]] = None
    bit_rate: Optional[Union[str, int]] = None
    probe_score: Optional[int] = None
    tags: Optional[Dict[str, Any]] = None


class FFProbeOutput(BaseModel):
    streams: Optional[List[FFProbeStream]] = []
    chapters: Optional[List[FFProbeChapter]] = []
    format: Optional[FFProbeFormat] = None


# API response schemas
class MediaStreamResponse(BaseModel):
    id: int
    index: int
    codec_name: Optional[str] = None
    codec_long_name: Optional[str] = None
    codec_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    bit_rate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    tags: Optional[Dict[str, Any]] = None
    disposition: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class MediaChapterResponse(BaseModel):
    id: int
    chapter_id: int
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    tags: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class MediaFileResponse(BaseModel):
    id: int
    filename: str
    filepath: str
    file_size: Optional[int] = None
    format_name: Optional[str] = None
    format_long_name: Optional[str] = None
    duration: Optional[float] = None
    bit_rate: Optional[int] = None
    nb_streams: Optional[int] = None
    tags: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    streams: List[MediaStreamResponse] = []
    chapters: List[MediaChapterResponse] = []

    class Config:
        from_attributes = True


class MediaFileCreate(BaseModel):
    filepath: str
    ffprobe_data: FFProbeOutput


class MediaStreamCreate(BaseModel):
    media_file_id: int
    index: int
    codec_name: Optional[str] = None
    codec_long_name: Optional[str] = None
    codec_type: Optional[str] = None
    codec_tag_string: Optional[str] = None
    codec_tag: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    coded_width: Optional[int] = None
    coded_height: Optional[int] = None
    closed_captions: Optional[bool] = None
    film_grain: Optional[bool] = None
    has_b_frames: Optional[int] = None
    sample_aspect_ratio: Optional[str] = None
    display_aspect_ratio: Optional[str] = None
    pix_fmt: Optional[str] = None
    level: Optional[int] = None
    color_range: Optional[str] = None
    color_space: Optional[str] = None
    color_transfer: Optional[str] = None
    color_primaries: Optional[str] = None
    chroma_location: Optional[str] = None
    field_order: Optional[str] = None
    refs: Optional[int] = None
    r_frame_rate: Optional[str] = None
    avg_frame_rate: Optional[str] = None
    time_base: Optional[str] = None
    sample_fmt: Optional[str] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    channel_layout: Optional[str] = None
    bits_per_sample: Optional[int] = None
    start_pts: Optional[int] = None
    start_time: Optional[float] = None
    duration_ts: Optional[int] = None
    duration: Optional[float] = None
    bit_rate: Optional[int] = None
    max_bit_rate: Optional[int] = None
    bits_per_raw_sample: Optional[int] = None
    nb_frames: Optional[int] = None
    nb_read_frames: Optional[int] = None
    nb_read_packets: Optional[int] = None
    disposition: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, Any]] = None


class MediaStreamUpdate(BaseModel):
    codec_name: Optional[str] = None
    codec_long_name: Optional[str] = None
    codec_type: Optional[str] = None
    codec_tag_string: Optional[str] = None
    codec_tag: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    coded_width: Optional[int] = None
    coded_height: Optional[int] = None
    closed_captions: Optional[bool] = None
    film_grain: Optional[bool] = None
    has_b_frames: Optional[int] = None
    sample_aspect_ratio: Optional[str] = None
    display_aspect_ratio: Optional[str] = None
    pix_fmt: Optional[str] = None
    level: Optional[int] = None
    color_range: Optional[str] = None
    color_space: Optional[str] = None
    color_transfer: Optional[str] = None
    color_primaries: Optional[str] = None
    chroma_location: Optional[str] = None
    field_order: Optional[str] = None
    refs: Optional[int] = None
    r_frame_rate: Optional[str] = None
    avg_frame_rate: Optional[str] = None
    time_base: Optional[str] = None
    sample_fmt: Optional[str] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    channel_layout: Optional[str] = None
    bits_per_sample: Optional[int] = None
    start_pts: Optional[int] = None
    start_time: Optional[float] = None
    duration_ts: Optional[int] = None
    duration: Optional[float] = None
    bit_rate: Optional[int] = None
    max_bit_rate: Optional[int] = None
    bits_per_raw_sample: Optional[int] = None
    nb_frames: Optional[int] = None
    nb_read_frames: Optional[int] = None
    nb_read_packets: Optional[int] = None
    disposition: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, Any]] = None


class FFProbeErrorResponse(BaseModel):
    id: int
    filepath: str
    error_message: Optional[str] = None
    error_code: Optional[int] = None
    attempted_at: datetime

    class Config:
        from_attributes = True
