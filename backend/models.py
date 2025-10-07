"""
Pydantic models for request/response validation
"""
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class ChannelRequest(BaseModel):
    """Request model for channel scraping"""
    channel_url: str = Field(..., description="YouTube channel URL")


class VideoMetadata(BaseModel):
    """Video metadata model"""
    id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Video title")
    duration: int = Field(..., description="Video duration in seconds")
    thumbnail: str = Field(..., description="Video thumbnail URL")
    url: str = Field(..., description="Full YouTube video URL")


class ScrapeResponse(BaseModel):
    """Response model for scrape endpoint"""
    videos: List[VideoMetadata] = Field(..., description="List of filtered videos")
    total_found: int = Field(..., description="Total videos found before filtering")
    filtered_count: int = Field(..., description="Number of videos after filtering")


class DownloadRequest(BaseModel):
    """Request model for download endpoint"""
    video_ids: List[str] = Field(..., description="List of video IDs to download")


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
    current_video: Optional[str] = Field(None, description="Title of current video being downloaded")
    completed_videos: List[str] = Field(default_factory=list, description="List of completed video titles")
    failed_videos: List[str] = Field(default_factory=list, description="List of failed video titles")


class FilesResponse(BaseModel):
    """Response model for files endpoint"""
    files: List[str] = Field(..., description="List of downloaded MP3 files")
    total: int = Field(..., description="Total number of files")
