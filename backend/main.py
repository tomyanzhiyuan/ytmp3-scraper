"""
FastAPI application for YouTube MP3 scraper
"""
#hello :)
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import logging

from models import (
    ChannelRequest,
    ScrapeResponse,
    VideoMetadata,
    DownloadRequest,
    DownloadResponse,
    DownloadProgress,
    FilesResponse
)
from video_scraper import scrape_channel_videos
from downloader import download_video_as_mp3, list_downloaded_files, get_output_directory, is_rate_limited, check_file_exists

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube MP3 Scraper API",
    description="API for scraping YouTube channels and downloading videos as MP3",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for download progress
download_state: Dict = {
    "current": 0,
    "total": 0,
    "percentage": 0.0,
    "status": "idle",
    "current_video": None,
    "completed_videos": [],
    "failed_videos": [],
    "video_map": {},  # Maps video IDs to metadata
    "channel_name": None  # Current channel name for organizing downloads
}

# Global state for scraping progress
scrape_state: Dict = {
    "status": "idle",  # idle, scraping, completed, error
    "total_videos": 0,
    "processed_videos": 0,
    "filtered_videos": 0,
    "current_video": None,
    "percentage": 0.0,
    "error": None,
    "result": None  # Final scrape result
}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "YouTube MP3 Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "scrape": "POST /api/scrape",
            "download": "POST /api/download",
            "progress": "GET /api/progress",
            "files": "GET /api/files"
        }
    }


async def scrape_channel_task(channel_url: str):
    """
    Background task to scrape channel videos.
    """
    scrape_state["status"] = "scraping"
    scrape_state["error"] = None
    scrape_state["result"] = None
    
    def progress_callback(total, processed, filtered, current_title):
        """Update scrape progress"""
        scrape_state["total_videos"] = total
        scrape_state["processed_videos"] = processed
        scrape_state["filtered_videos"] = filtered
        scrape_state["current_video"] = current_title
        scrape_state["percentage"] = (processed / total * 100) if total > 0 else 0
    
    try:
        # Scrape videos with progress callback
        channel_name, videos = scrape_channel_videos(channel_url, progress_callback)
        
        # Store channel name and video metadata in global state for later download
        download_state["channel_name"] = channel_name
        logger.info(f"📁 Stored channel name for downloads: '{channel_name}'")
        
        for video in videos:
            download_state["video_map"][video["id"]] = video
        
        # Store result
        scrape_state["result"] = {
            "channel_name": channel_name,
            "videos": videos
        }
        scrape_state["status"] = "completed"
        scrape_state["current_video"] = None
        
        logger.info(f"Scraping completed: {len(videos)} videos found for channel '{channel_name}'")
        
    except Exception as e:
        logger.error(f"Error in scrape task: {str(e)}")
        scrape_state["status"] = "error"
        scrape_state["error"] = str(e)


@app.post("/api/scrape")
async def scrape_channel(request: ChannelRequest, background_tasks: BackgroundTasks):
    """
    Start scraping a YouTube channel in the background.
    Returns immediately and client should poll /api/scrape-progress for updates.
    
    Filters:
    - Duration > 60 seconds
    - Excludes YouTube Shorts
    - Excludes livestreams
    """
    try:
        logger.info(f"Received scrape request for: {request.channel_url}")
        
        # Validate URL
        if not request.channel_url or "youtube.com" not in request.channel_url:
            raise HTTPException(status_code=400, detail="Invalid YouTube channel URL")
        
        # Check if already scraping
        if scrape_state["status"] == "scraping":
            raise HTTPException(status_code=409, detail="Scraping already in progress")
        
        # Start background scraping task
        background_tasks.add_task(scrape_channel_task, request.channel_url)
        
        return {"message": "Scraping started", "status": "scraping"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in scrape endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scrape-progress")
async def get_scrape_progress():
    """
    Get current scraping progress.
    """
    response = {
        "status": scrape_state["status"],
        "total_videos": scrape_state["total_videos"],
        "processed_videos": scrape_state["processed_videos"],
        "filtered_videos": scrape_state["filtered_videos"],
        "current_video": scrape_state["current_video"],
        "percentage": scrape_state["percentage"],
        "error": scrape_state["error"]
    }
    
    # If completed, include the result
    if scrape_state["status"] == "completed" and scrape_state["result"]:
        response["result"] = scrape_state["result"]
    
    return response


async def download_videos_task(video_ids: list):
    """
    Background task to download videos with exponential backoff for rate limiting.
    """
    import time
    import random
    
    download_state["status"] = "downloading"
    download_state["current"] = 0
    download_state["total"] = len(video_ids)
    download_state["completed_videos"] = []
    download_state["failed_videos"] = []
    
    # Configuration
    MAX_RETRIES = 4
    BASE_DELAY = 5.0  # Increased from 2s to 5s
    MAX_DELAY = 15.0  # Maximum random delay
    
    for idx, video_id in enumerate(video_ids, 1):
        retry_count = 0
        success = False
        
        # Get video metadata
        video_data = download_state["video_map"].get(video_id)
        if not video_data:
            logger.warning(f"Video metadata not found for ID: {video_id}")
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            title = video_id
        else:
            video_url = video_data["url"]
            title = video_data["title"]
        
        download_state["current"] = idx
        download_state["current_video"] = title
        download_state["percentage"] = (idx / len(video_ids)) * 100
        
        # PRE-CHECK: Check if file already exists BEFORE making any API calls
        channel_name = download_state.get("channel_name")
        
        # Debug logging
        if idx == 1:  # Log once at start
            logger.info(f"📁 Using channel name for downloads: '{channel_name}'")
            if channel_name:
                logger.info(f"📂 Files will be saved to: output/{channel_name}/")
            else:
                logger.warning("⚠️  No channel name set! Files will be saved to: output/")
        
        file_exists, existing_path = check_file_exists(title, channel_name)
        
        if file_exists:
            logger.info(f"✓ Already downloaded ({idx}/{len(video_ids)}): {title}")
            download_state["completed_videos"].append(title)
            success = True
            # Skip to next video immediately (no delay needed for skipped files)
            continue
        
        # Retry loop with exponential backoff
        while retry_count < MAX_RETRIES and not success:
            try:
                if retry_count > 0:
                    logger.info(f"Retry {retry_count}/{MAX_RETRIES-1} for: {title}")
                else:
                    logger.info(f"Downloading {idx}/{len(video_ids)}: {title}")
                
                # Download video with channel name for subfolder organization
                output_file = download_video_as_mp3(video_url, channel_name=channel_name)
                
                download_state["completed_videos"].append(title)
                logger.info(f"Successfully downloaded: {title}")
                success = True
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error downloading {title}: {error_msg}")
                
                # Check if rate limited
                is_limited, suggested_wait = is_rate_limited(error_msg)
                
                if is_limited and retry_count < MAX_RETRIES - 1:
                    # Calculate exponential backoff
                    # Start with suggested wait or base delay
                    if suggested_wait > 0:
                        wait_time = suggested_wait
                    else:
                        # Exponential backoff: 5min, 15min, 30min, 60min
                        wait_time = 300 * (3 ** retry_count)  # 300s = 5 minutes
                    
                    logger.warning(f"⚠️  Rate limited! Waiting {wait_time/60:.1f} minutes before retry...")
                    logger.info(f"Progress: {len(download_state['completed_videos'])}/{len(video_ids)} completed, {idx-len(download_state['completed_videos'])}/{len(video_ids)} remaining")
                    
                    # Update status to show waiting
                    download_state["current_video"] = f"⏳ Waiting {wait_time/60:.0f}min (rate limited)"
                    
                    # Wait with progress updates every minute
                    for remaining in range(int(wait_time), 0, -60):
                        time.sleep(min(60, remaining))
                        if remaining > 60:
                            download_state["current_video"] = f"⏳ Waiting {remaining/60:.0f}min (rate limited)"
                    
                    retry_count += 1
                    download_state["current_video"] = title  # Restore title
                    logger.info(f"Resuming downloads after rate limit wait...")
                    
                else:
                    # Not rate limited or max retries reached
                    download_state["failed_videos"].append(title)
                    if is_limited:
                        logger.error(f"Max retries reached for {title}. Moving to next video.")
                    break
        
        # Add delay between downloads (with random jitter to appear more human)
        if idx < len(video_ids) and success:
            delay = random.uniform(BASE_DELAY, MAX_DELAY)
            logger.info(f"Waiting {delay:.1f}s before next download...")
            time.sleep(delay)
    
    # Update final status
    download_state["status"] = "completed"
    download_state["current_video"] = None
    download_state["percentage"] = 100.0
    
    logger.info(f"✅ Download task completed!")
    logger.info(f"Success: {len(download_state['completed_videos'])}/{len(video_ids)}")
    logger.info(f"Failed: {len(download_state['failed_videos'])}/{len(video_ids)}")


@app.post("/api/download", response_model=DownloadResponse)
async def download_videos(request: DownloadRequest, background_tasks: BackgroundTasks):
    """
    Download selected videos as MP3 files.
    Downloads happen in the background.
    """
    try:
        if not request.video_ids:
            raise HTTPException(status_code=400, detail="No video IDs provided")
        
        if download_state["status"] == "downloading":
            raise HTTPException(status_code=409, detail="Download already in progress")
        
        logger.info(f"Starting download for {len(request.video_ids)} videos")
        
        # Start background download task
        background_tasks.add_task(download_videos_task, request.video_ids)
        
        return DownloadResponse(
            message="Download started",
            total=len(request.video_ids)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in download endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/progress", response_model=DownloadProgress)
async def get_progress():
    """
    Get current download progress.
    """
    return DownloadProgress(
        current=download_state["current"],
        total=download_state["total"],
        percentage=download_state["percentage"],
        status=download_state["status"],
        current_video=download_state["current_video"],
        completed_videos=download_state["completed_videos"],
        failed_videos=download_state["failed_videos"]
    )


@app.get("/api/files", response_model=FilesResponse)
async def get_files():
    """
    List all downloaded MP3 files.
    """
    try:
        files = list_downloaded_files()
        return FilesResponse(
            files=files,
            total=len(files)
        )
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/output-dir")
async def get_output_dir():
    """
    Get the output directory path.
    """
    return {
        "output_directory": get_output_directory()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
