"""
Pydantic models for request/response validation
"""

from enum import Enum

from pydantic import BaseModel, Field


class VideoType(str, Enum):
    """Video type filter options"""

    ALL = "all"  # Both shorts and long videos
    SHORTS = "shorts"  # Only shorts
    VIDEOS = "videos"  # Only long-form videos


class TimeFrame(str, Enum):
    """Time frame filter options"""

    ALL = "all"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class DownloadFormat(str, Enum):
    """Download format options"""

    MP3 = "mp3"
    MP4 = "mp4"


class ChannelRequest(BaseModel):
    """Request model for channel scraping"""

    channel_url: str = Field(..., description="YouTube channel URL")
    video_type: VideoType = Field(default=VideoType.VIDEOS, description="Filter by video type")
    time_frame: TimeFrame = Field(default=TimeFrame.ALL, description="Filter by time frame")


class VideoMetadata(BaseModel):
    """Video metadata model"""

    id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Video title")
    duration: int = Field(..., description="Video duration in seconds")
    thumbnail: str = Field(..., description="Video thumbnail URL")
    url: str = Field(..., description="Full YouTube video URL")


class ScrapeResponse(BaseModel):
    """Response model for scrape endpoint"""

    videos: list[VideoMetadata] = Field(..., description="List of filtered videos")
    total_found: int = Field(..., description="Total videos found before filtering")
    filtered_count: int = Field(..., description="Number of videos after filtering")


class DownloadRequest(BaseModel):
    """Request model for download endpoint"""

    video_ids: list[str] = Field(..., description="List of video IDs to download")
    format: DownloadFormat = Field(default=DownloadFormat.MP3, description="Download format (mp3 or mp4)")


class DownloadResponse(BaseModel):
    """Response model for download endpoint"""

    message: str = Field(..., description="Status message")
    total: int = Field(..., description="Total number of videos to download")


class DownloadProgress(BaseModel):
    """Progress tracking model"""

    current: int = Field(..., description="Current video number being downloaded")
    total: int = Field(..., description="Total videos to download")
    percentage: float = Field(..., description="Completion percentage")
    status: str = Field(..., description="Current status (idle, downloading, completed, error)")
    current_video: str | None = Field(None, description="Title of current video being downloaded")
    completed_videos: list[str] = Field(default_factory=list, description="List of completed video titles")
    failed_videos: list[str] = Field(default_factory=list, description="List of failed video titles")


class FilesResponse(BaseModel):
    """Response model for files endpoint"""

    files: list[str] = Field(..., description="List of downloaded files (MP3/MP4)")
    total: int = Field(..., description="Total number of files")
