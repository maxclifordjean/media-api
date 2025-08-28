from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    Float,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from .database import Base


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    file_size = Column(Integer)
    format_name = Column(String)
    format_long_name = Column(String)
    duration = Column(Float)  # in seconds
    bit_rate = Column(Integer)
    probe_score = Column(Integer)
    start_time = Column(Float)
    nb_streams = Column(Integer)
    nb_programs = Column(Integer)
    tags = Column(JSON)  # Store format tags as JSON
    raw_ffprobe = Column(JSON)  # Store complete ffprobe output
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    streams = relationship(
        "MediaStream", back_populates="media_file", cascade="all, delete-orphan"
    )
    chapters = relationship(
        "MediaChapter", back_populates="media_file", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<MediaFile(filename='{self.filename}', duration={self.duration})>"


class MediaStream(Base):
    __tablename__ = "media_streams"

    id = Column(Integer, primary_key=True, index=True)
    media_file_id = Column(Integer, ForeignKey("media_files.id"), nullable=False)
    index = Column(Integer, nullable=False)  # Stream index from ffprobe
    codec_name = Column(String)
    codec_long_name = Column(String)
    codec_type = Column(String)  # video, audio, subtitle, data, attachment
    codec_tag_string = Column(String)
    codec_tag = Column(String)

    # Video specific fields
    width = Column(Integer)
    height = Column(Integer)
    coded_width = Column(Integer)
    coded_height = Column(Integer)
    closed_captions = Column(Boolean)
    film_grain = Column(Boolean)
    has_b_frames = Column(Integer)
    sample_aspect_ratio = Column(String)
    display_aspect_ratio = Column(String)
    pix_fmt = Column(String)
    level = Column(Integer)
    color_range = Column(String)
    color_space = Column(String)
    color_transfer = Column(String)
    color_primaries = Column(String)
    chroma_location = Column(String)
    field_order = Column(String)
    refs = Column(Integer)
    r_frame_rate = Column(String)
    avg_frame_rate = Column(String)
    time_base = Column(String)

    # Audio specific fields
    sample_fmt = Column(String)
    sample_rate = Column(Integer)
    channels = Column(Integer)
    channel_layout = Column(String)
    bits_per_sample = Column(Integer)

    # Common stream fields
    start_pts = Column(Integer)
    start_time = Column(Float)
    duration_ts = Column(Integer)
    duration = Column(Float)
    bit_rate = Column(Integer)
    max_bit_rate = Column(Integer)
    bits_per_raw_sample = Column(Integer)
    nb_frames = Column(Integer)
    nb_read_frames = Column(Integer)
    nb_read_packets = Column(Integer)

    # Disposition flags
    disposition = Column(JSON)  # Store disposition as JSON
    tags = Column(JSON)  # Store stream tags as JSON

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    media_file = relationship("MediaFile", back_populates="streams")

    def __repr__(self):
        return f"<MediaStream(index={self.index}, codec_type='{self.codec_type}', codec_name='{self.codec_name}')>"


class MediaChapter(Base):
    __tablename__ = "media_chapters"

    id = Column(Integer, primary_key=True, index=True)
    media_file_id = Column(Integer, ForeignKey("media_files.id"), nullable=False)
    chapter_id = Column(Integer, nullable=False)  # Chapter ID from ffprobe
    time_base = Column(String)
    start = Column(Integer)
    start_time = Column(Float)
    end = Column(Integer)
    end_time = Column(Float)
    tags = Column(JSON)  # Store chapter tags as JSON (title, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    media_file = relationship("MediaFile", back_populates="chapters")

    def __repr__(self):
        return f"<MediaChapter(id={self.chapter_id}, start_time={self.start_time}, end_time={self.end_time})>"


class FFProbeError(Base):
    __tablename__ = "ffprobe_errors"

    id = Column(Integer, primary_key=True, index=True)
    filepath = Column(String, nullable=False)
    error_message = Column(Text)
    error_code = Column(Integer)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return (
            f"<FFProbeError(filepath='{self.filepath}', error_code={self.error_code})>"
        )
